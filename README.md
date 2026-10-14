# Strands Travel Agent

Agente de viajes inteligente desarrollado con **Strands Agents y AWS**. Permite consultar información sobre vuelos, clima y actividades turísticas mediante un agente de IA que combina herramientas externas con recuperación de información usando RAG.

## Objetivo del proyecto

Desarrollar un agente inteligente capaz de asistir al usuario en la planificación de viajes mediante consultas en lenguaje natural, integrando servicios de AWS, herramientas externas y una base de conocimiento para generar respuestas contextualizadas.

## Descripción general

El agente interpreta las preguntas del usuario y selecciona las herramientas necesarias para responder. Puede consultar opciones de vuelos, obtener información meteorológica y recuperar información turística desde documentos almacenados en una base de conocimiento.

Además, conserva el historial de las conversaciones para mantener el contexto de cada sesión.

## Arquitectura

```text
                         Usuario
                            |
                            v
                 AWS Lambda + Strands Agents
                            |
              +-------------+--------------+
              |             |              |
              v             v              v
        Búsqueda de     Consulta del    Recuperación
          vuelos          clima       de conocimiento
                                           |
                                           v
                               Amazon Bedrock Knowledge Bases
                                           |
                                           v
                                       Amazon S3

                 Amazon DynamoDB
              (historial de sesiones)
```

## Componentes y servicios de AWS

| Servicio o componente | Función |
|---|---|
| Strands Agents | Orquesta el agente y coordina el uso de herramientas. |
| AWS Lambda | Ejecuta la lógica del agente sin administrar servidores. |
| Amazon Bedrock | Proporciona el modelo de IA Nova Lite para generar respuestas. |
| Amazon Bedrock Knowledge Bases | Recupera información relevante de los documentos mediante RAG. |
| Amazon S3 | Almacena los documentos de la base de conocimiento. |
| Amazon DynamoDB | Conserva el historial de las sesiones. |
| AWS IAM | Administra los permisos de acceso entre los servicios. |
| AWS SAM y AWS CloudFormation | Permiten construir y desplegar la aplicación y su infraestructura. |
| Amazon CloudWatch | Permite consultar registros de ejecución y diagnosticar errores. |

## Flujo de funcionamiento

1. El usuario envía una consulta en lenguaje natural.
2. Strands Agents interpreta la solicitud y determina qué herramienta utilizar.
3. El agente consulta la herramienta de vuelos, la fuente meteorológica o la base de conocimiento, según la necesidad.
4. Para las consultas turísticas, Bedrock Knowledge Bases recupera información relevante de los documentos almacenados en S3.
5. El modelo utiliza la información obtenida para generar una respuesta.
6. El historial de la conversación se conserva en DynamoDB.

## Tecnologías utilizadas

- Python
- Strands Agents
- Amazon Bedrock — Nova Lite
- Amazon Bedrock Knowledge Bases (RAG)
- AWS Lambda
- Amazon S3
- Amazon DynamoDB
- AWS SAM y AWS CloudFormation

## Demostración

[Ver video de demostración del proyecto](https://wgcp-my.sharepoint.com/:v:/g/personal/sofia_gordillo_blend360_com/IQClskNjqfX4RIBrDJfQzXmdAYBvVR7Z_uNEOmYXWX-VcZc?e=H52EI6)