#Api ChatCSV


# Mera Chat

Este proyecto esta ideado para mediante RAG poder realizar consultas en lenguaje natural acerca de la informacion de cada campaña con tal de, ante una duda en llamado, poder contestarla basandose en la documentacion de la forma mas exacta

## API Reference

#### Cambiar contraseña

```http
  Post /change_password/
```

| Parameter | Type     | Description                |
| :-------- | :------- | :------------------------- |
| `documento` | `int` | **Required**. Documento del usuario a ser modificado |
| `password`  | `string`|**Required**. Contraseña actual, o vacio en caso de no tener una|
| `new_password`|`string`|**Required**. Nueva contraseña|

returns: Mesaje de satifactorio

#### Obtener token

La autenticación se realiza a través de JSON Web Token: https://jwt.io/introduction/. Una primer llamada de autenticación de credenciales devolverá un Token, que por la duración de la sesión podrá ser utilizado para consumir la información de la API.
Una vez obtenido el Token, basta incluirlo en llamadas posteriores en la cabecera Authorization (Authorization header), utilizando el schema Bearer.
Authorization: Bearer <token>

```http
  Post /token/
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `username`  | `int` | **Required**. Id of item to fetch |
| `password`  | `string`|**Required**.

returns: diccionario con token y tipo de token

#### Realizar consulta

```http
  Post /consultar/
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `bearer Token`      | `string` | **Required**. Token de autenticacion |
| `query`|`string`|**Required**. Consulta a realizar|

returns: Json con response, la respuesta a la pregunta y el user, usuario que la realizo


```http
  Post /consultar/
```

| Parameter | Type     | Description                       |
| :-------- | :------- | :-------------------------------- |
| `bearer Token`      | `string` | **Required**. Token de autenticacion |
| `query`|`string`|**Required**. Consulta a realizar|

returns: Json con response, la respuesta a la pregunta, context, con toda la informacio que se utilizo para la consulta y el user, usuario que la realizo
