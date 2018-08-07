"""Custom exceptions """



class InvalidAmountError(ValueError):
    def __init__(self):
        super().__init__('Invalid amount for currency')

class CurrencyMismatchError(ValueError):
    def __init__(self):
        super().__init__('Currencies must match')

class InvalidOperandError(ValueError):
    def __init__(self):
        super().__init__('Invalid operand types for operation')
