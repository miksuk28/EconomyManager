login = {
    "type": "object",
    "properties": {
        "username":     {"type": "string"},
        "password":     {"type": "string"}
    },
    "required": ["username", "password"]
}


create_receipt = {
    "type": "object",
    "properties": {
        "desription":   {"type": "string"},
        "date":         {"type": "string"},
        "products": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "name":         {"type": "string"},
                    "price":        {"type": "number"},
                    "quantity":     {"type": "number"},
                    "category_id":  {
                        "anyOf": [
                            {"type": "integer"},
                            {"type": "null"}
                        ]
                    }
                },
                "required": ["name", "price", "quantity", "category_id"]
            }
        }
    },
    "required": ["products"]
}