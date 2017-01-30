#!./venv/bin/python3

# file: src/money_re.py

import re
import src.config as config

DEFAULT_CURRENCY = config.DEFAULTS["currency"]

CURRENCY_SIGNS = {     # The dollar sign must be escaped because
    "dollar": "[$]",   # it's to be used in a RegEx expression,
    "pound": "[£]",    # so all are being excaped (made into a
    "yuan": "[¥]",     # character class) to make processing
    "yen": "[¥]",      # simpler.  The square brackets are stripped
    "euro": "[€]",     # when not wanted.
    "rupee": "[₹]",   
    }    # Multicharacter currency signs are not supported at present.

RE_EXPRESSION_SANS_CURRENCY_SYMBOL = r"""
{0:}?  # Optional currency sign.
(   # Option to use minus to indicate negativity.
    [-]?  # Could be a negative number.
    {0:}?  # Currency sign could come after minus

    (  # Beginning of first digit section.
        (  # Forces at least one digit before decimal.
            \d+
            [.]  # Must contain a decimal place.
            \d{{0,2}}  # 0 ... 2 digits after decimal.
        )  #            ^
        |  #  OR: digit ^before or v after mandatory decimal.
        (  # Forces at least one digit after decimal.
            \d*
            [.]  # Must contain a decimal place.
            \d{{1,2}}  # 1 or 2 digits after decimal.
        )
    )  # End of first digit section.
)  # Ends minus sign option.
|
(  # Next choice is to use parens for negativity.
    (?P<parens>  # Presence of this named group means negative.
        [(]  # Presence of the parens indicates negativity.
        {0:}?  # Currency sign could be inside parens.
          # following OR is a duplicate of what's above.
        (  # Begin digit section for second time.
            (
                \d+  # Forces at least one digit before decimal.
                [.]  # Must contain a decimal place.
                \d{{0,2}}  # 0 ... 2 digits after decimal.
            )
            |
            (
                \d*  # Forces at least one digit after decimal.
                [.]  # Must contain a decimal place.
                \d{{1,2}}  # 1 or 2 digits after decimal.
            )
        )  # End of the second appearance of this digit section.
        [)]  # This closing parens DOES NOT get included!!!
        # ... & I don't understand why not.
    ) # Closes named group 'parens'.
) # Closes outer OR (provides parens functionality.)
"""

_match = ''
_parens = ''

def pull_money(source, 
            currency_name = DEFAULT_CURRENCY,
            re_prototype=RE_EXPRESSION_SANS_CURRENCY_SYMBOL,
            debug=False):
    """
    Uses RE to pull out a monetary value.
    If a money quantity is not found, returns None.
    If successfull, returns a 2 part tuple:
        1. the money value as a float.
        2. the span where re matched (a two part tuple.)
    Uses globals _match and _parens for debugging purposes.
    Negative values may be indicated by either a minus sign or by
    enclosing parentheses.
    The specified currency symbol may be used and it may appear on
    either side of the minus sign or opening parens.
    <escaped_currency_sign> must be a currency sign within square
    brackets. e.g. "[£]"
    """
    escaped_currency_sign=CURRENCY_SIGNS[currency_name]
    global _match, _parens
    re_expression = (RE_EXPRESSION_SANS_CURRENCY_SYMBOL
                        .format(escaped_currency_sign))
    money_pattern = re.compile(re_expression, re.VERBOSE)
    ret = None
    match = money_pattern.search(source)
    if match:
        _match = match.group()
        span = match.span()
        try:
            _parens = match.group("parens")
#           if debug:
#               print("'parens': {}".format(_parens))
        except IndexError:
            _parens = False
        if _parens:
            ret = _parens.replace("(","-")
            ret = ret.replace(")","")
        else:
            ret = match.group()
#       print("DEBUG: 'ret' is {}".format(ret))
        ret = float(ret.replace(escaped_currency_sign[1:-1], ''))
    else:
        ret = _match = match
    # We still have the float value in ret.
    if ret:
        return (ret, (span))


def test():
    """Testing suite: run if module is run as __main__.
    """
    failures = []
    source = (
        ("Expect failure.", "-4.00"),
        ("Price 13.87 of something", "13.87"),
        ("Price -23.87 of something", "-23.87"),
        ("Price $-23.87 of something", "-23.87"),
        ("Price -$23.87 of something", "-23.87"),
        ("1010 .37 Cr", "0.37"),
        ("1010 $.37 Cr", "0.37"),
        ("1010 -$.37 Cr", "-0.37"),
        ("1010 $-.37 Cr", "-0.37"),
        ("4.", "4.00"), ("$4.", "4.00"),
        ("-$4.", "-4.00"), ("$-4.", "-4.00"),
        ("($4.)", "-4.00"), ("$(4.)", "-4.00"),
        ("1010 (5.37) Cr", "-5.37"),
        ("1010 Dr ($88.4)", "-88.40"),
        ("Dr 1010 ($88.4)", "-88.40"),
        ("Dr $(98.4) 1010", "-98.40"), 

(".3 1010 Dr", "0.30"), ("$.3 1010 Dr", "0.30"),
("-.3 1010 Dr", "-0.30"), ("(.3) 1010 Dr", "-0.30"),
("-$.3 1010 Dr", "-0.30"), ("$-.3 1010 Dr", "-0.30"),
("($.3) 1010 Dr", "-0.30"), ("$(.3) 1010 Dr", "-0.30"), 

        ("EXPECT FAILURE", None),
    )
    from tests.money_test_data import more_tests
    source = source + more_tests

    print("{:<30} {:<10} {:<10} {:<10}"
        .format("SOURCE", "MATCH", "RESULT", "EXPECTED"))

    for source, expected in source:
        returned = pull_money(source, debug=True)
        if returned:
            value, span = returned
            if "{:.2f}".format(value) != expected:
                add_info = ("!!  '{}' !>> '{}'  !!"
                                .format(_match, expected))
            else:
                add_info = ''
            print("{:<30} {:<10} {:<10.2f} {:<10} {}"
                .format(source, _match, value, expected, add_info))
        else:
            failures.append("{:<30} {}".format(source, expected))

    if failures:
        print("\nFAILURES:")
        print("{:<30} {}".format('Source', 'Expected'))
        print("{:<30} {}".format('------', '--------'))
        print("\n".join(failures))


if __name__ == "__main__":
    test()

