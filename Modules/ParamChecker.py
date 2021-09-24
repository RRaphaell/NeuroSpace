def is_number(x):
    try:
        float(x)
        return True
    except ValueError:
        return None


class ParamChecker:
    def __init__(self, param_value, param_name):
        self._param_value = param_value
        self._param_name = param_name

    @property
    def number(self):
        if not is_number(self._param_value):
            raise ValueError(f'Parameter "{self._param_name}" should be number')
        return self

    @property
    def not_empty(self):
        if self._param_value == "":
            raise ValueError(f'Please enter "{self._param_name}" value')
        return self

    @property
    def positive(self):
        if float(self._param_value) < 0:
            raise ValueError(f'Parameter "{self._param_name}" should be positive')
        return self

    @property
    def value(self):
        return float(self._param_value)
