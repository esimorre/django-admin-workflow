from django.contrib.contenttypes.models import ContentType

from django_admin_workflow.models import get_workflow_contenttypes


def get_target_ctype(app_model):
    ctype, wf_ready, explicit = None, False, False
    q = get_workflow_contenttypes()
    ctypes = list(ContentType.objects.filter(q))
    if app_model and len(app_model) > 0:
        app, mod = app_model[0].split('.')
        ctype = ContentType.objects.get_by_natural_key(app, mod)
        if ctype in ctypes: wf_ready = True
        explicit = True
    else:
        if ctypes:
            ctype = ctypes[0]
            wf_ready = True
    return ctype, wf_ready, explicit, len(ctypes)

def get_fields_model(ctype, joined=" , "):
    cls = ctype.model_class()
    fields = set()
    for f in [ff.attname for ff in cls._meta.fields]:
        if f in ('pk', 'id'): continue
        fv = f.replace('_id', '')
        fields.add(fv)
    if not joined: return fields
    return joined.join(["'%s'" % f for f in fields])
