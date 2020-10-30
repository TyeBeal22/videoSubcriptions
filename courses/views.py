from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404
from django.views import generic
from django.core.files.base import ContentFile
from django.utils.text import slugify
from django.utils.timezone import now
from django.views.generic import ListView, DetailView, View, FormView, RedirectView, TemplateView
from django.views.generic.detail import SingleObjectMixin
from membership.models import UserMembership
from .models import Course, Lesson, Video
from django_anysign import api as django_anysign
from django_docusign import api as django_docusign
from docusign_esign import EnvelopesApi, RecipientViewRequest, Document, Signer, EnvelopeDefinition, SignHere, Tabs, \
    Recipients

try:
    from django.urls import reverse
except ImportError:
    from django.core.urlresolvers import reverse


def get_access_code(request):

    base_url = "https://account-d.docusign.com/oauth/auth"
    auth_url = "{0}?response_type=code&scope=signature&client_id={1}&redirect_uri={2}".format(
        base_url, CLIENT_AUTH_ID, request.build_absolute_url(reverse('auth_login')))

    return HttpResponseRedirect(auth_url)


def auth_login(request):

    base_url = "https://account-d.docusign.com/oauth/token"
    auth_code_string = '{0}:{1}'.format(CLIENT_AUTH_ID, CLIENT_SECRET_KEY)
    auth_token = base64.b64encode(auth_code_string.encode())

    req_headers = {"Authorization": "Basic {0}".format(
        auth_token.decode('utf-8'))}
    post_data = {'grant_type': 'authorization_code',
                 'code': request.GET.get('code')}

    r = requests.post(base_url, date=post_date, headers=req_headers)

    response = r.json()

    if not 'error' in response:
        return HttpResponseRedirect("{0}?token={1}".format(reverse('get_signing_url'), response['access_token']))

    return HttpResponse(response['error'])


def embedded_signing_ceremony(request):
    signer_email = 'tyebeal@yahoo.com'
    signer_name = 'Tye Beal'

    with open(os.path.join(BASE_DIR, 'static/', 'SoftwareLicenseSPA.pdf'), "rb") as file:
        content_bytes = file.read()
    base64_file_content = base64.b64encode(content_bytes).decode('ascii')

    document = Document(
        document_base64=base64_file_content,
        name='SoftwareLicenseSPA',
        file_extension='pdf',
        document_id=1
    )

    signer = Signer(
        email=signer_email, name=signer_name, recipient_id="1", routing_order="1",
        client_user_id=client_user_id,
    )

    sign_here = SignHere(
        document_id='1', page_number='1', recipient_id='1', tab_label='SignHereTab',
        x_position='195', y_position='147'
    )

    signer.tabs = Tabs(sign_here_tabs=[sign_here])

    envelope_definition = EnvelopeDefinition(
        email_subject="Please sign this document",
        documents=[document],
        recipients=Recipients(signers=[signer]),
        status="sent"
    )

    api_client = ApiClient()
    api_client.host = base_path
    api_client.set_default_header(
        "Authorization", "Bearer " + request.GET.get('token'))

    envelope_api = EnvelopesApi(api_client)
    results = envelope_api.create_envelope(
        account_id, envelope_definition=envelope_definition)

    envelope_id = results.envelope_id
    recipient_view_request = RecipientViewRequest(
        authetication_method='none', client_user_id=client_user_id,
        recipient_id='1', return_url=request.build_absolute_url(reverse('sign_completd')),
        user_name=signer_name, email=signer_email
    )

    results = envelope_api.create_recipient_view(account_id, envelope_id,
                                                 recipient_view_request=recipient_view_request
                                                 )
    return HttpResponse(results.url)


def sign_complete(request):

    return HttpResponse('Signing Completed successfully')


class CourseListView(ListView):
    model = Course


class CourseDetailView(DetailView):
    model = Course


class LessonDetailView(LoginRequiredMixin, View):

    def get(self, request, course_slug, lesson_slug, *args, **kwargs):
        course = get_object_or_404(Course, slug=course_slug)
        lesson = get_object_or_404(Lesson, slug=lesson_slug)
        user_membership = get_object_or_404(UserMembership, user=request.user)
        user_membership_type = user_membership.membership.membership_type
        course_allowed_mem_types = course.allowed_memberships.all()
        context = {'object': None}
        if course_allowed_mem_types.filter(membership_type=user_membership_type).exists():
            context = {'object': lesson}
        return render(request, "courses/lesson_detail.html", context)


class VideoDetailView(generic.DetailView):

    template_name = "courses/video_detail.html"
