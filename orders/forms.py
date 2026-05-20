from django import forms


class CheckoutForm(forms.Form):
    full_name = forms.CharField(max_length=120)
    email = forms.EmailField()
    phone = forms.RegexField(regex=r"^\d{10,15}$", error_messages={"invalid": "Enter a valid 10-15 digit phone number."})
    shipping_address = forms.CharField(widget=forms.Textarea(attrs={"rows": 4}))
    shipping_city = forms.CharField(max_length=80)
    shipping_state = forms.CharField(max_length=80)
    shipping_postal_code = forms.RegexField(regex=r"^[A-Za-z0-9\- ]{4,12}$")
    payment_method = forms.ChoiceField(choices=[("razorpay", "Razorpay"), ("cod", "Cash on Delivery")])
