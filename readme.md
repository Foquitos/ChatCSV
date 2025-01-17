# Mera Chat

**Mera Chat** es un proyecto diseñado para utilizar **Retrieval-Augmented Generation (RAG)** con el fin de realizar consultas en lenguaje natural sobre la información de cada campaña. Esto permite responder con precisión y rapidez a cualquier duda basada en la documentación relevante.

---

## API Reference

### Cambiar contraseña

Permite cambiar la contraseña a algun usuario seleccionado, o generar la misma en caso de que el documento este en la nomina y no tenga registrado alguna otra

**Endpoint:**  
`POST /change_password/`

**Parámetros:**

| Nombre         | Tipo      | Descripción                                               |
|----------------|-----------|-----------------------------------------------------------|
| `documento`    | `int`     | **Requerido.** Documento del usuario a modificar.         |
| `password`     | `string`  | **Requerido.** Contraseña actual, o vacío si no la tiene. |
| `new_password` | `string`  | **Requerido.** Nueva contraseña.                          |

**Respuesta:**  
Mensaje de confirmación en caso de éxito.

---

### Obtener token

La autenticación se realiza mediante **JSON Web Token (JWT)**.  
Para iniciar sesión, se debe realizar una primera llamada con credenciales válidas. Esto generará un token que puede ser utilizado para acceder a los demás recursos de la API durante la sesión.

**Endpoint:**  
`POST /token/`

**Parámetros:**

| Nombre      | Tipo      | Descripción                             |
|-------------|-----------|-----------------------------------------|
| `username`  | `int`     | **Requerido.** Nombre de usuario o ID.  |
| `password`  | `string`  | **Requerido.** Contraseña del usuario.  |

**Respuesta:**  
Un diccionario con los siguientes datos:  
- `token`: Token generado.  
- `token_type`: Tipo de token (por ejemplo, "Bearer").  

**Uso del Token:**  
Incluye el token en el encabezado de autorización en las siguientes solicitudes:  
`Authorization: Bearer <token>`

### Realizar consulta

Permite realizar una consulta basada en la información disponible

**Endpoint:**  
`POST /consultar/`

**Parámetros:**

| Nombre      | Tipo      | Descripción                             |
|-------------|-----------|-----------------------------------------|
| `bearer Token`  | `string`     | **Requerido.** Token de autenticación.  |
| `query`  | `string`  | **Requerido.** Consulta a realizar.  |
| `campana`  | `string`  | **Requerido.** Campaña a la cual se le quiere realizar consultas, actualmente solo CSV.  |

**Respuesta:**  
Un diccionario con los siguientes datos:  
- `response`: Respuesta a la consulta.  
- `user`: Usuario que realizó la consulta.  

### Realizar consulta con contexto

Proporciona información adicional sobre el contexto utilizado para responder la consulta

**Endpoint:**  
`POST /consultar_contexto/`

**Parámetros:**

| Nombre      | Tipo      | Descripción                             |
|-------------|-----------|-----------------------------------------|
| `bearer Token`  | `string`     | **Requerido.** Token de autenticación.  |
| `query`  | `string`  | **Requerido.** Consulta a realizar.  |
| `campana`  | `string`  | **Requerido.** Campaña a la cual se le quiere realizar consultas, actualmente solo CSV.  |

**Respuesta:**  
Un diccionario con los siguientes datos:  
- `response`: Respuesta a la consulta.  
- `context`: Información utilizada para generar la respuesta.  
- `user`: Usuario que realizó la consulta.  

## Notas adicionales

- Asegúrate de mantener tu token seguro, ya que este permite acceso a los recursos de la API.  
- La contraseña debe cumplir con las políticas de seguridad definidas para garantizar la protección de los usuarios.  
- Consulta la documentación completa o contacta al equipo de soporte en caso de dudas.
