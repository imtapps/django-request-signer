
*********************
Request Signer Server
*********************

Creating a Client Id and Private Key
====================================

#. Add 'request_signer' to INSTALLED_APPS in your Django settings file.
#. Log into the Django Admin.
#. Navigate to "/request_signer/authorizedclient/add/".
#. Choose a Client Id and save the generated Private Key.
#. That's it! Now you have everything you need to be able to talk to your server.



Requiring a valid signature for views
=====================================

To require a valid signature for a view use the **signature_required** decorator

Function based views

::

    from request_signer.decorators import signature_required

    @signature_required
    def myview(request):
        pass

Class based views

::

    from request_signer.decorators import signature_required

    url(r'sample/',  signature_required(views.MyView.as_view())),

