
$(document).ready(function() {
    $(".fee-payment-total input").blur(function () {
        var payment_total = parse_decimal(this.value);
        var discount_rate = parse_decimal($('.fee-discount-rate input').val()).dividedBy(100);
        var discount = parse_decimal($('.fee-discount input').val());
        this.value = payment_total.toFormat(2);

        var balance = new BigNumber('0.00');
        $(".fee-row").each(function () {
            var month_amount = parse_decimal($('.fee-amount', this).text());

            // apply discount_rate
            if (!discount_rate.isZero()) {
                month_amount = month_amount.minus(discount_rate.times(month_amount));
                $('.fee-discount', this).text(month_amount.toFormat(2));
            } else {
                $('.fee-discount', this).text('');
            }

            var payment = payment_total.greaterThanOrEqualTo(month_amount) ? month_amount : payment_total;

            // apply discount
            var month_discount = new BigNumber('0.00');
            if (payment.lessThan(month_amount) && !discount.isZero()) {
                month_discount = discount.greaterThanOrEqualTo(month_amount.minus(payment)) ?
                    month_amount.minus(payment) : discount;
                month_amount = month_amount.minus(month_discount);
                discount = discount.minus(month_discount);
                $('.fee-discount', this).text(month_amount.toFormat(2));
            }

            // add classes to rows
            if (payment.equals(month_amount)) {
                $(this).addClass('table-success').removeClass('table-warning');
            } else if (payment.isZero() && month_discount.isZero()) {
                $(this).removeClass('table-success table-warning');
            } else {
                $(this).addClass('table-warning').removeClass('table-success');
                if (!discount_rate.isZero() || !month_discount.isZero()) {
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
    });

    $(".fee-discount-rate input").blur(function () {
        var discount_rate = parse_decimal(this.value);
        this.value = discount_rate.toFormat(0);
        if (!discount_rate.isZero()) {
            $('.fee-discount input').val('');
        }
        $(".fee-payment-total input").blur();
    });

    $(".fee-discount input").blur(function () {
        var discount = parse_decimal(this.value);
        this.value = discount.toFormat(2);
        if (!discount.isZero()) {
            $('.fee-discount-rate input').val('');
        }
        $(".fee-payment-total input").blur();
    });
});
