
$(document).ready(function() {
    $("#id_amount").blur(function () {
        var amount = parse_decimal(this.value);
        var discount_rate = parse_decimal($('#id_discount_rate').val()).dividedBy(100);
        var discount = parse_decimal($('#id_discount').val());
        if (!amount.isZero()) {
            this.value = amount.toFixed(2);
        }

        // reset colors
        var rows = $('.fee-row');
        rows.removeClass('table-warning table-success');

        var balance = new BigNumber('0.00');
        var payment_total = new BigNumber('0.00');
        rows.each(function () {
            var month_amount = parse_decimal($('.fee-amount', this).text());
            var month_discount = new BigNumber('0.00');

            // apply discount
            if (!discount_rate.isZero()) {
                month_discount = discount_rate.times(month_amount);
            } else if (!discount.isZero() && amount.lessThan(month_amount)) {
                month_discount = discount.greaterThanOrEqualTo(month_amount.minus(amount)) ?
                    month_amount.minus(amount) : discount;
                discount = discount.minus(month_discount);
            }
            month_amount = month_amount.minus(month_discount);
            var payment = amount.greaterThanOrEqualTo(month_amount) ? month_amount : amount;

            amount = amount.minus(payment);
            balance = balance.add(month_amount).minus(payment);
            payment_total = payment_total.add(payment);

            // add classes to rows
            if (payment.equals(month_amount)) {
                $(this).addClass('table-success');
            } else if (!payment.isZero()) {
                $(this).addClass('table-warning');
            }

            $('.fee-balance', this).text(balance.toFormat(2));
            $('.fee-payment', this).text(payment.toFormat(2));
            $('.fee-discount', this).text(month_discount.toFormat(2));
        });
        $('.fee-balance-total').text(balance.toFormat(2));
        $('.fee-payment-total').text(payment_total.toFormat(2));
    }).blur();

    $("#id_discount_rate").blur(function () {
        var discount_rate = parse_decimal(this.value);
        if (!discount_rate.isZero()) {
            this.value = discount_rate.toFixed(0);
            $('#id_discount').val('');
        }
        $("#id_amount").blur();
    });

    $("#id_discount").blur(function () {
        var discount = parse_decimal(this.value);
        if (!discount.isZero()) {
            this.value = discount.toFixed(2);
            $('#id_discount_rate').val('');
        }
        $("#id_amount").blur();
    });

    $('#id_date').datepicker({dateFormat: "yy-mm-dd"});
});
