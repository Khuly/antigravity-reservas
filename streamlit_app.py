import os
import sys

# Asegurar que el directorio raíz esté en el path para las importaciones
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Ejecutar la aplicación principal dentro de ui/
from ui.web_app import main

if __name__ == "__main__":
    main()