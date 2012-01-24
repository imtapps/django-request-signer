from django import test
from request_signer.admin import AuthorizedClientForm

class AdminAuthorizedClientFormTests(test.TestCase):

    def test_sets_private_key_widget_to_readonly(self):
        form = AuthorizedClientForm()
        self.assertEqual('readonly', form.fields['private_key'].widget.attrs['readonly'])

    def test_sets_private_key_widget_is_styled(self):
        form = AuthorizedClientForm()
        self.assertEqual('width: 300px; background-color: #ccc;', form.fields['private_key'].widget.attrs['style'])
