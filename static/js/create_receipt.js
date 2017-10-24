$(document).ready(function() {
    $(".fee-payment-total input").blur(function () {
        var payment_total = parse_decimal(this.value);
        this.value = payment_total.toFormat(2);
        console.log(payment_total.toString());

        var balance = new BigNumber('0.00');
        $(".fee-row").each(function () {
            var month_amount = parse_decimal($('.fee-amount', this).text());
            var payment = payment_total.greaterThanOrEqualTo(month_amount) ? month_amount : payment_total;
            payment_total = payment_total.minus(payment);
            balance = balance.add(month_amount).minus(payment);

            $('.fee-balance', this).text(balance.toFormat(2));
            $('.fee-payment', this).text(payment.toFormat(2));
        });
        $('.fee-balance-total').text(balance.toFormat(2));
    });
});
