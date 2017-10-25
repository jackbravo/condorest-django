
$(document).ready(function() {
    $(".fee-payment-total input").blur(function () {
        var payment_total = parse_decimal(this.value);
        var discount_rate = parse_decimal($('.fee-discount-rate input').val()).dividedBy(100);
        this.value = payment_total.toFormat(2);

        var balance = new BigNumber('0.00');
        var discount_total = new BigNumber('0.00');
        $(".fee-row").each(function () {
            var month_amount = parse_decimal($('.fee-amount', this).text());
            if (!discount_rate.isZero()) {
                month_amount = month_amount.minus(discount_rate.times(month_amount));
                discount_total = discount_total.add(month_amount);
                $('.fee-discount', this).text(month_amount.toFormat(2));
            } else {
                $('.fee-discount', this).text('');
            }

            var payment = payment_total.greaterThanOrEqualTo(month_amount) ? month_amount : payment_total;
            if (payment.equals(month_amount)) {
                $(this).addClass('table-success').removeClass('table-warning');
            } else if (payment.isZero()) {
                $(this).removeClass('table-success table-warning');
            } else {
                $(this).addClass('table-warning').removeClass('table-success');
                if (!discount_rate.isZero()) {
                    $('.discount-row').addClass('table-danger');
                } else {
                    $('.discount-row').removeClass('table-danger');
                }
            }

            payment_total = payment_total.minus(payment);
            balance = balance.add(month_amount).minus(payment);

            $('.fee-balance', this).text(balance.toFormat(2));
            $('.fee-payment', this).text(payment.toFormat(2));
        });
        $('.fee-balance-total').text(balance.toFormat(2));
        $('.fee-discount-total').text(discount_total.toFormat(2));
    });

    $(".fee-discount-rate input").blur(function () {
        var payment_total_input = $(".fee-payment-total input");
        var payment_total = parse_decimal(payment_total_input.val());
        if (!payment_total.isZero()) {
            var discount_rate = parse_decimal(this.value);
            this.value = discount_rate.toFormat(0);
            discount_rate = parse_decimal(this.value).dividedBy(100);
            var payment_and_discount = payment_total.dividedBy(discount_rate.minus(1).negated());
            $('.fee-discount input').val(payment_and_discount.minus(payment_total).toFormat(2));
            payment_total_input.blur();
        }
    });

    $(".fee-discount input").blur(function () {
        var payment_total_input = $(".fee-payment-total input");
        var payment_total = parse_decimal(payment_total_input.val());
        if (!payment_total.isZero()) {
            var discount = parse_decimal(this.value);
            this.value = discount.toFormat(2);
            var payment_and_discount = payment_total.add(discount);
            $('.fee-discount-rate input').val(payment_total.times(100).dividedBy(payment_and_discount).minus(100).negated().toFormat(0));
            payment_total_input.blur();
        }
    });
});
