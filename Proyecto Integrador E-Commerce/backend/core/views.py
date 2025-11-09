import hashlib
import hmac

import mercadopago
import logging
from django.conf import settings
from rest_framework import viewsets, status, generics
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from .models import Categoria, Curso, Instructor, Leccion, Inscripcion, ItemCarrito, Carrito, Pedido, ItemPedido
from .serializers import (
    CategoriaSerializer, InstructorSerializer, LeccionSerializer, EmptySerializer,
    CursoListSerializer, CursoDetailSerializer, CarritoSerializer, PedidoSerializer
)
from .permissions import IsAdminOrReadOnly, CanViewLessons


class CategoriaViewSet(viewsets.ModelViewSet):
    queryset = Categoria.objects.all()
    serializer_class = CategoriaSerializer
    permission_classes = [IsAdminOrReadOnly]


class InstructorViewSet(viewsets.ModelViewSet):
    queryset = Instructor.objects.all()
    serializer_class = InstructorSerializer
    permission_classes = [IsAdminUser]


class CursoViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAdminOrReadOnly]

    def get_queryset(self):
        """
        Si el usuario es staff/admin, muestra todos los cursos.
        Si no, muestra solo los publicados.
        """
        if self.request.user.is_staff:
            return Curso.objects.all()
        return Curso.objects.filter(publicado=True)

    def get_serializer_class(self):
        """
        Elige qué serializer usar basado en la acción solicitada.
        """
        if self.action == 'list':
            # Para la lista de cursos, usa el serializer ligero.
            return CursoListSerializer
        if self.action == 'inscribir':
            return EmptySerializer
        # Para cualquier otra acción (retrieve, create, update), usa el de detalle.
        return CursoDetailSerializer

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def inscribir(self, request, pk=None):
        """
        Endpoint para que un usuario autenticado se inscriba en este curso.
        """
        curso = self.get_object()
        usuario = request.user
        if Inscripcion.objects.filter(usuario=usuario, curso=curso).exists():
            return Response(
                {'error': 'Ya estás inscrito en este curso.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        Inscripcion.objects.create(usuario=usuario, curso=curso)
        return Response(
            {'status': 'Inscripción exitosa.'},
            status=status.HTTP_201_CREATED
        )

    @action(detail=True, methods=['delete'], permission_classes=[IsAuthenticated])
    def desinscribir(self, request, pk=None):
        """
        Endpoint para que un usuario autenticado se desinscriba de este curso.
        """
        curso = self.get_object()
        usuario = request.user
        try:
            inscripcion = Inscripcion.objects.get(usuario=usuario, curso=curso)
            inscripcion.delete()
            return Response(
                {'status': 'Desinscripción exitosa.'},
                status=status.HTTP_200_OK
            )
        except Inscripcion.DoesNotExist:
            return Response(
                {'error': 'No estás inscrito en este curso.'},
                status=status.HTTP_404_NOT_FOUND
            )


class LeccionViewSet(viewsets.ModelViewSet):
    serializer_class = LeccionSerializer
    permission_classes = [CanViewLessons]

    def get_queryset(self):
        curso_pk = self.kwargs['curso_pk']
        return Leccion.objects.filter(curso_id=curso_pk)

    def perform_create(self, serializer):
        curso_pk = self.kwargs['curso_pk']
        curso = Curso.objects.get(pk=curso_pk)
        serializer.save(curso=curso)


class MisCursosView(generics.ListAPIView):
    """
    Endpoint de solo lectura para los cursos del usuario autenticado.
    """
    # Se cambia el serializer al de lista para que sea más eficiente.
    serializer_class = CursoListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        usuario_actual = self.request.user
        return Curso.objects.filter(inscritos__usuario=usuario_actual)

class CarritoViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestionar el carrito del usuario autenticado.
    """
    serializer_class = CarritoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # The model uses `completado` to mark finished carts; return active (not completed) carts
        return Carrito.objects.filter(usuario=self.request.user, completado=False)

    def list(self, request, *args, **kwargs):
        """
        Devuelve el carrito activo del usuario o lo crea si no existe.
        """
        carrito, created = Carrito.objects.get_or_create(
            usuario=request.user,
            completado=False
        )
        serializer = self.get_serializer(carrito)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='agregar')
    def agregar(self, request, pk=None):
        """
        Agrega un curso al carrito (o incrementa si ya existe).
        """
        carrito = self.get_object()
        curso_id = request.data.get('curso_id')

        if not curso_id:
            return Response({'error': 'Se requiere curso_id'}, status=status.HTTP_400_BAD_REQUEST)

        item, creado = ItemCarrito.objects.get_or_create(
            carrito=carrito,
            curso_id=curso_id,
            defaults={'cantidad': 1}
        )
        if not creado:
            item.cantidad += 1
            item.save()

        return Response({'status': 'Curso agregado al carrito'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='quitar')
    def quitar(self, request, pk=None):
        """
        Quita un curso del carrito.
        """
        carrito = self.get_object()
        curso_id = request.data.get('curso_id')

        try:
            item = ItemCarrito.objects.get(carrito=carrito, curso_id=curso_id)
            item.delete()
            return Response({'status': 'Curso quitado del carrito'}, status=status.HTTP_200_OK)
        except ItemCarrito.DoesNotExist:
            return Response({'error': 'El curso no está en el carrito'}, status=status.HTTP_404_NOT_FOUND)

    @action(detail=True, methods=['post'], url_path='vaciar')
    def vaciar(self, request, pk=None):
        carrito = self.get_object()
        carrito.vaciar()
        return Response({'status': 'Carrito vaciado'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['post'], url_path='checkout')
    def checkout(self, request, pk=None):
        """
        Genera una preferencia de pago con los ítems del carrito activo del usuario.
        """
        carrito = self.get_object()

        if not carrito.items.exists():
            return Response({'error': 'El carrito está vacío'}, status=status.HTTP_400_BAD_REQUEST)

        # Crear la preferencia con los ítems del carrito
        sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)

        items = []
        for item in carrito.items.all():
            items.append({
                "title": item.curso.titulo,
                "quantity": item.cantidad,
                "unit_price": float(item.curso.precio),
            })

        # notification_url: MercadoPago will POST notifications here (webhook)
        notification_url = request.build_absolute_uri(f"/api/v1/webhook/mercadopago/")

        # For auto_return to work MercadoPago requires a valid back_urls.success
        # that points to a web page (frontend). We'll set back_urls to the
        # frontend success/failure pages so MP accepts auto_return, and rely on
        # the webhook (`notification_url`) to process the enrollment server-side.
        frontend_success = f"{settings.FRONTEND_URL_RAILWAY}/payments/success/{carrito.id}/"
        frontend_failure = f"{settings.FRONTEND_URL_RAILWAY}/payments/failure/{carrito.id}/"

        preference_data = {
            "items": items,
            "back_urls": {
                # Use frontend URLs so MercadoPago can auto-return the user
                "success": frontend_success,
                "failure": frontend_failure,
            },
            "notification_url": notification_url,
            "auto_return": "approved",
            "external_reference": str(carrito.id),
        }

        try:
            preference_response = sdk.preference().create(preference_data)
        except Exception as e:
            # Log and return a useful error so the frontend can show a message
            print('Error creating MercadoPago preference:', e)
            return Response({'error': 'preference_creation_failed', 'details': str(e)}, status=status.HTTP_502_BAD_GATEWAY)

        preference = preference_response.get('response') if isinstance(preference_response, dict) else None

        # Validate structure returned by SDK
        if not preference or 'id' not in preference or 'init_point' not in preference:
            print('Unexpected preference response from MercadoPago:', preference_response)
            return Response({'error': 'invalid_preference_response', 'details': preference_response}, status=status.HTTP_502_BAD_GATEWAY)

        return Response({
            "preference_id": preference["id"],
            "init_point": preference["init_point"],
        }, status=status.HTTP_201_CREATED)


# ------------------------------------------------------------------
# Endpoints para manejar el retorno desde MercadoPago
# ------------------------------------------------------------------
from django.http import HttpResponse, HttpResponseBadRequest, HttpResponseNotAllowed, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
import json

logger = logging.getLogger(__name__)

@csrf_exempt
def mercadopago_webhook(request):
    """
    Endpoint para recibir notificaciones (IPN) de MercadoPago.
    Valida la firma de la petición ANTES de procesar el pago.
    """
    if request.method != 'POST':
        return HttpResponseNotAllowed(['POST'])

    # --- INICIO DE VALIDACIÓN DE FIRMA ---

    # 1. Obtener tu clave secreta de settings
    secret = settings.MERCADOPAGO_WEBHOOK_SECRET
    if not secret:
        logger.error('MERCADOPAGO_WEBHOOK_SECRET no está configurada en settings.')
        return JsonResponse({'error': 'server configuration error'}, status=500)

    # 2. Obtener los headers de la petición
    signature_header = request.headers.get('x-signature')
    request_id_header = request.headers.get('x-request-id')

    if not signature_header or not request_id_header:
        logger.warning('Webhook recibido sin headers x-signature o x-request-id')
        return HttpResponseBadRequest('Missing required headers')

    # 3. Parsear el header x-signature para obtener 'ts' y 'v1'
    try:
        parts = signature_header.split(',')
        ts = v1_hash = None
        for part in parts:
            key, value = part.split('=', 1)
            if key == 'ts':
                ts = value
            elif key == 'v1':
                v1_hash = value

        if not ts or not v1_hash:
            raise ValueError("Formato de x-signature inválido")

    except Exception as e:
        logger.warning(f'Error parseando x-signature: {e}')
        return HttpResponseBadRequest('Invalid x-signature format')

    # 4. Obtener el payment_id (CORRECCIÓN para UnboundLocalError)
    payment_id = None  # Inicializar
    try:
        # Primero desde query params (V2)
        payment_id = request.GET.get('data.id') or request.GET.get('id')

        if not payment_id:
            # Si no, desde el body (V1)
            try:
                payload = json.loads(request.body.decode('utf-8'))
                if isinstance(payload, dict):
                    data = payload.get('data') or {}
                    if isinstance(data, dict):
                        payment_id = data.get('id')
                    if not payment_id:
                        payment_id = payload.get('id')
            except Exception:
                logger.info('No JSON body found or invalid JSON.')

        if not payment_id:
            logger.warning('No payment id (data.id) found in query params or body. Query: %s', request.GET)
            return HttpResponseBadRequest('No payment id found')

    except Exception as e:
        logger.exception('Error grave al parsear el request del webhook: %s', e)
        return JsonResponse({'ok': False, 'error': 'request parsing failed'}, status=200)

    # 5. Crear el "manifest" o plantilla de firma
    manifest_template = f"id:{payment_id};request-id:{request_id_header};ts:{ts};"

    # 6. Calcular la firma HMAC-SHA256
    calculated_hash = hmac.new(
        secret.encode('utf-8'),
        msg=manifest_template.encode('utf-8'),
        digestmod=hashlib.sha256
    ).hexdigest()

    # 7. Comparar de forma segura la firma calculada con la recibida (v1)
    if not hmac.compare_digest(calculated_hash, v1_hash):
        logger.error(f'Firma de Webhook inválida. Calculada: {calculated_hash}, Recibida: {v1_hash}')
        return JsonResponse({'error': 'invalid signature'}, status=403)  # 403 Forbidden

    logger.info(f'Firma de Webhook validada exitosamente para payment_id: {payment_id}')

    # --- FIN DE VALIDACIÓN DE FIRMA ---

    # --- INICIO DE LÓGICA DE PROCESAMIENTO ---

    sdk = mercadopago.SDK(settings.MERCADOPAGO_ACCESS_TOKEN)
    try:
        payment_resp = sdk.payment().get(payment_id)
        payment_info = payment_resp.get('response', {})
        logger.info('mercadopago_webhook fetched payment id=%s', payment_id)
    except Exception as e:
        logger.exception('Error fetching MP payment for id=%s: %s', payment_id, e)
        # Devolver 200 para evitar reintentos infinitos
        return JsonResponse({'ok': False, 'error': 'payment fetch failed'}, status=200)

    # Buscar external_reference que contiene el carrito id
    external_reference = payment_info.get('external_reference')
    try:
        carrito_id = int(external_reference) if external_reference else None
    except Exception:
        carrito_id = None

    # Determinar si pago aprobado (CORRECCIÓN para AttributeError 'int')
    status_val = payment_info.get('status') or payment_info.get('collection_status') or ''
    status_mp = str(status_val).lower()  # Convertir a string ANTES de .lower()

    logger.info('mercadopago_webhook payment_id=%s external_reference=%s status=%s', payment_id, external_reference,
                status_mp)

    if not carrito_id:
        logger.warning('mercadopago_webhook: missing external_reference in payment %s', payment_id)
        return JsonResponse({'ok': False, 'reason': 'missing external_reference'}, status=200)

    if status_mp != 'approved':
        # No aprobado: devolver 200 para confirmar recepción
        logger.info('mercadopago_webhook: payment %s not approved (status=%s)', payment_id, status_mp)
        return JsonResponse({'ok': True, 'processed': False, 'status': status_mp}, status=200)

    # Procesar: crear Pedido, ItemPedido e Inscripciones
    try:
        carrito = Carrito.objects.get(pk=carrito_id)
    except Carrito.DoesNotExist:
        logger.warning('mercadopago_webhook: carrito %s not found', carrito_id)
        return JsonResponse({'ok': False, 'reason': 'carrito not found'}, status=200)

    # Evitar procesar dos veces: si carrito ya está completado, devolvemos ok
    if carrito.completado:
        logger.info('mercadopago_webhook: carrito %s already completed; skipping', carrito_id)
        return JsonResponse({'ok': True, 'processed': False, 'reason': 'already completed'}, status=200)

    items = list(carrito.items.all())
    logger.info('Processing webhook for carrito=%s items=%d', carrito_id, len(items))
    pedido = Pedido.objects.create(usuario=carrito.usuario, completado=True)
    created_inscriptions = []

    for item in items:
        ItemPedido.objects.create(pedido=pedido, curso=item.curso, precio_compra=item.curso.precio)

        # Crear inscripción si no existe
        if not Inscripcion.objects.filter(usuario=carrito.usuario, curso=item.curso).exists():
            Inscripcion.objects.create(usuario=carrito.usuario, curso=item.curso)
            created_inscriptions.append(item.curso.id)
        else:
            logger.info('mercadopago_webhook: user %s already enrolled in curso %s', carrito.usuario_id, item.curso.id)

    # Marcar carrito como completado
    carrito.vaciar()
    carrito.completado = True
    carrito.save()
    logger.info('Webhook processed carrito=%s created_inscriptions=%s pedido=%s', carrito_id, created_inscriptions,
                pedido.id)

    return JsonResponse({'ok': True, 'processed': True, 'created': created_inscriptions}, status=200)