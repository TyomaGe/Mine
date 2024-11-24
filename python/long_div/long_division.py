#!/usr/bin/env python3

def check_parameters(dividend, divider):
    if not isinstance(dividend, int):
        return "Dividend must be an integer"
    if not isinstance(divider, int):
        return "Divider must be an integer"
    if divider == 0:
        return "Division by 0"
    return None


def make_res_str(quotient, temp_calcs, dividend_str, divider_str):
    result = dividend_str + "|" + divider_str + "\n"
    index = 0
    spaces = 0
    is_remainder_requires = True
    for temp_calculation in temp_calcs:
        temp_dividend, incompl_dividend, remainder = (
            temp_calculation[0], temp_calculation[1], temp_calculation[2])
        if index == 0:
            if temp_dividend - incompl_dividend != 0:
                spaces += len(str(incompl_dividend)) - len(str(remainder))
            else:
                if len(str(temp_dividend)) - 1 > 0:
                    spaces += len(str(temp_dividend)) - 1
                else:
                    spaces += 1
            if incompl_dividend == 0:
                result += str(remainder) + "|" + "0"
                is_remainder_requires = False
            else:
                result += (str(incompl_dividend) + (
                        len(dividend_str) - len(str(incompl_dividend))) * " "
                           + "|" + quotient.lstrip("0") + "\n")
        else:
            if incompl_dividend != 0:
                result += spaces * " " + str(temp_dividend) + "\n"
                spaces += len(str(temp_dividend)) - len(str(incompl_dividend))
                result += spaces * " " + str(incompl_dividend) + "\n"
                if temp_dividend - incompl_dividend != 0:
                    spaces += len(str(incompl_dividend)) - len(str(remainder))
                else:
                    if len(str(temp_dividend)) - 1 > 0:
                        spaces += len(str(temp_dividend)) - 1
                    else:
                        spaces += 1
            else:
                if remainder != 0:
                    spaces = len(dividend_str) - len(str(remainder))
                else:
                    continue
        index += 1
    if is_remainder_requires:
        if spaces == len(dividend_str):
            spaces -= 1
        result += " " * spaces + str(temp_calcs[-1][2])
    return result


def long_division(dividend, divider):
    error_check = check_parameters(dividend, divider)
    if error_check is not None:
        return error_check
    dividend_str = str(dividend)
    divider_str = str(divider)
    quotient = ""
    remainder = 0
    temp_calcs = []
    temp_dividend = 0
    index = 0
    for digit in dividend_str:
        temp_dividend = remainder * 10 + int(digit)
        temp_quotient = temp_dividend // divider
        quotient += str(temp_quotient)
        incompl_dividend = temp_quotient * divider
        remainder = temp_dividend % divider
        if temp_quotient != 0 or index == len(dividend_str) - 1:
            temp_calcs.append((temp_dividend, incompl_dividend, remainder))
        index += 1
    return make_res_str(quotient, temp_calcs, dividend_str, divider_str)


def main():
    print(long_division(123, 123))
    print()
    print(long_division(1, 1))
    print()
    print(long_division(15, 3))
    print()
    print(long_division(3, 15))
    print()
    print(long_division(12345, 25))
    print()
    print(long_division(1234, 1423))
    print()
    print(long_division(87654532, 1))
    print()
    print(long_division(24600, 123))
    print()
    print(long_division(4567, 1234567))
    print()
    print(long_division(246001, 123))
    print()
    print(long_division(123456789, 531))
    print()
    print(long_division(425934261694251, 12345678))


if __name__ == '__main__':
    main()
