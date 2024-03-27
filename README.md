# HULK-Compiler

## Configuración del entorno virtual

Primero, clona este repositorio en tu máquina local. Luego, navega a la carpeta del proyecto y crea un entorno virtual:

Para Windows:

```bash
python -m venv venv
```

Para macOS y Linux:

```bash
python3 -m venv venv
```

## Activación del entorno virtual

Para Windows:

```bash
.\venv\Scripts\activate
```

Para macOS y Linux:

```bash
source venv/bin/activate
```

## Instalación de dependencias

Finalmente, instala las dependencias del proyecto ejecutando:

```bash
pip install -r requirements.txt
```

Para llevar las bibliotecas del entorno al `requirements.txt`, haz lo siguiente:

```bash
pip freeze > requirements.txt
```

## Ejecutar Tester

Para ejecutar los tests, simplemente basta con ejecutar, para cada archivo, lo siguiente:

Para lexer_test.py:

```bash
python -m unittest -v test.lexer_tests
```

Esto ejecutará todos los tests del lexer. Si, por el contrario, quieres ejecutar un método específico a la vez, puedes hacerlo de la siguiente manera:

```bash
python -m unittest -v test.lexer_tests.TestLexer.<metodo>
```

Donde <metodo> debe ser reemplazado por el nombre del método de test que deseas ejecutar.
