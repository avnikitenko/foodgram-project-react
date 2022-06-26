from rest_framework_csv.renderers import CSVRenderer


class CartRender(CSVRenderer):
    header = ['name', 'sum', 'measurement_unit']
