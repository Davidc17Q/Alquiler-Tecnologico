# TechRent - Plataforma de alquiler de equipos tecnológicos

Proyecto Django + Django REST Framework organizado con arquitectura limpia en capas:

- `domain/`: entidades del dominio y patrones creacionales (Builder).
- `application/`: servicios de aplicación, lógica de negocio y puertos (interfaces).
- `infrastructure/`: implementación de modelos Django, repositorios e integraciones (pasarelas de pago).
- `presentation/`: capa de exposición HTTP (API REST con DRF).
- `config/`: configuración del proyecto Django.

El objetivo es desacoplar la lógica de negocio de los detalles de infraestructura (ORM, HTTP, pasarela de pagos), favoreciendo SRP, DIP y alta cohesión.

