from rest_framework import serializers

from .models import PaymentInvoice, PaymentDetail, Withdraw


class PaymentInvoiceSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = PaymentInvoice
        fields = '__all__'


class PaymentDetailSerializer(serializers.ModelSerializer):
    amount = serializers.ReadOnlyField()
    paid_at = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    class Meta:
        model = PaymentDetail
        fields = '__all__'


class PaymentResultSerializer(serializers.Serializer):
    invoice_number = serializers.CharField(max_length=50)
    invoice_date = serializers.CharField(max_length=50)
    trx_reference_id = serializers.CharField(max_length=50)


class WithdrawSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
        fields = '__all__'


class WithdrawPublicSerializer(serializers.ModelSerializer):
    class Meta:
        model = Withdraw
        fields = [
            'amount',
            'transaction_date',
            'transaction_code',
        ]


class WithdrawRequestSerializer(serializers.Serializer):
    shop = serializers.IntegerField()
    amount = serializers.IntegerField()
    sheba = serializers.CharField(max_length=30)
    full_name = serializers.CharField(max_length=80)
