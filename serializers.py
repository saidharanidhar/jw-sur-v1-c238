from marshmallow import Schema, fields, EXCLUDE


class GeoLite(Schema):
    city = fields.String(data_key="geoplugin_city", allow_none=True)
    ip = fields.String(data_key="geoplugin_request", allow_none=True)
    region = fields.String(data_key="geoplugin_region", allow_none=True)
    latitude = fields.Float(data_key="geoplugin_latitude", allow_none=True)
    timezone = fields.Float(data_key="geoplugin_timezone", allow_none=True)
    longitude = fields.Float(data_key="geoplugin_longitude", allow_none=True)
    countryName = fields.String(data_key="geoplugin_countryName", allow_none=True)
    countryCode = fields.String(data_key="geoplugin_countryCode", allow_none=True)

    class Meta:
        unknown = EXCLUDE

