from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import time
from selenium.webdriver.support.ui import Select
from dotenv import load_dotenv  
import os
import datetime
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.action_chains import ActionChains

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

# Leer las variables de entorno
USER = os.getenv('MY_USER')
PASSWORD = os.getenv('MY_PASSWORD')
MONTH = os.getenv('MONTH')
ITERATIONS = int(os.getenv('ITERATIONS', 1))  # Número de iteraciones
detalle_precio = os.getenv("AMOUNT")
boton_valor = os.getenv("COMPANY")
fecha_comprobante = os.getenv("BILL_DATE")
fecha_desde = os.getenv("FROM_DATE")
fecha_hasta = os.getenv("TO_DATE")
fecha_expiracion = os.getenv("EXPIRATION_DATE")
DETALLE_DESCRIPCION = os.getenv("DESCRIPTION_DETAIL")



# Función para obtener el primer día hábil del mes
def get_first_weekday(year, month):
    first_day = datetime.date(year, month, 1)
    while first_day.weekday() == 6:  # Evita domingos
        first_day += datetime.timedelta(days=1)
    return first_day

# Función para obtener el quinto día hábil del mes siguiente
def get_fifth_weekday_of_next_month(year, month):
    # Mover al siguiente mes
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1
    # Primer día del próximo mes
    first_day_next_month = datetime.date(next_year, next_month, 1)
    weekday_count = 0
    # Encuentra el quinto día hábil
    while weekday_count < 5:
        if first_day_next_month.weekday() < 5:  # Si es día hábil (lunes a viernes)
            weekday_count += 1
        first_day_next_month += datetime.timedelta(days=1)
    return first_day_next_month - datetime.timedelta(days=1)

# Obtener el año actual
year = datetime.datetime.now().year
month = int(MONTH.strip())

# Obtener el primer día hábil del mes
first_weekday = get_first_weekday(year, month)
formatted_first_weekday = first_weekday.strftime('%d/%m/%Y')

# Obtener la fecha de vencimiento (quinto día hábil del mes siguiente)
vencimiento_pago = get_fifth_weekday_of_next_month(year, month)
formatted_vencimiento_pago = vencimiento_pago.strftime('%d/%m/%Y')

# Ejecutar las iteraciones
for iteration in range(ITERATIONS):
    # Calcula las fechas dinámicas para el campo "desde" y "hasta"
    desde_date = first_weekday + datetime.timedelta(days=iteration * 3)  # Evitar solapamiento de días
    hasta_date = desde_date + datetime.timedelta(days=2)  # Dos días después de "desde"

    # Formatea las fechas para Selenium
    formatted_desde_date = desde_date.strftime('%d/%m/%Y')
    formatted_hasta_date = hasta_date.strftime('%d/%m/%Y')

    # Configurar el WebDriver para Chrome
    driver = webdriver.Chrome()
    driver.get("https://auth.afip.gob.ar/contribuyente_/login.xhtml")

    # Introduce el CUIT en el cuadro de texto
    username_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'F1:username'))
    )
    username_input.send_keys(USER)

    # Haz clic en el botón "Siguiente"
    next_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'F1:btnSiguiente'))
    )
    next_button.click()

    # Introduce la contraseña
    password_input = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, 'F1:password'))
    )
    password_input.send_keys(PASSWORD)

    # Haz clic en el botón "Ingresar"
    login_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, 'F1:btnIngresar'))
    )
    login_button.click()

    # Resto de acciones para navegar hasta la sección de facturación omitido...
            # Espera hasta que el elemento "Monotributo" esté presente y haz clic en él
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='col-xs-12 col-md-15']//h3[text()='Monotributo']"))
    )
    a_element = element.find_element(By.XPATH, "./ancestor::a")
    a_element.click()

    # Espera hasta que se abra la segunda pestaña y cambia el contexto a ella
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
    driver.switch_to.window(driver.window_handles[1])

    # Espera hasta que el botón "Emitir Factura" esté presente y haz clic en él
    emitir_factura_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[@id='bBtn1' and contains(@class, 'btn-success') and contains(text(), 'Emitir Factura')]"))
    )
    emitir_factura_button.click()

    # Espera hasta que se abra la tercera pestaña y cambia el contexto a ella
    WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(3))
    driver.switch_to.window(driver.window_handles[2])

    empresa_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, f"//input[@type='button' and @value='{boton_valor}']"))
    )
    empresa_button.click()

    # Espera hasta que el botón "Generar Comprobantes" esté presente y haz clic en él
    generar_comprobantes_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@id='btn_gen_cmp']"))
    )
    generar_comprobantes_button.click()

    # Manejo del botón "Cerrar"
    try:
        close_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@id='novolveramostrar' and @type='button' and @value='Cerrar']"))
        )
        close_button.click()
    except TimeoutException:
        print("El botón de cerrar no está presente. Continuando con el siguiente paso...")

    # Resto del código para completar el proceso
# Espera hasta que el punto de venta esté presente y selecciona la opción
    try:
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'puntodeventa'))
        )
        select = Select(select_element)
        select.select_by_index(1)  # Selecciona la opción por índice
    except TimeoutException:
        print("No se pudo encontrar el punto de venta.")
    except NoSuchElementException as e:
        print(f"Error: {e}")
    time.sleep(2)
    #seleccionar factura c
    try:
        # Espera a que el elemento esté presente y visible
        select_element = WebDriverWait(driver, 10).until(
            EC.visibility_of_element_located((By.ID, 'universocomprobante'))
        )
        
        # Asegúrate de que el elemento sea interactuable
        WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, 'universocomprobante'))
        )
        
        # Selecciona el elemento de la lista desplegable
        select = Select(select_element)
        select.select_by_value('2')  # Selecciona "Factura C"
        print("Tipo de comprobante seleccionado: Factura C")
        
    except TimeoutException:
        print("No se pudo encontrar el menú de tipo de comprobante o el elemento no es interactuable.")
    except NoSuchElementException as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Se produjo un error: {e}")
    # Haz clic en el botón "Continuar" y espera que la nueva pantalla se cargue
    try:
        continuar_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='button' and @value='Continuar >']"))
        )
        continuar_button.click()
        
        # Espera a que la nueva pantalla se cargue completamente antes de buscar el campo de fecha
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.ID, 'fc'))
        )
    except TimeoutException:
        print("No se pudo encontrar el botón 'Continuar >' o la nueva pantalla no se cargó.")
    except NoSuchElementException as e:
        print(f"Error: {e}")

    # Rellena el campo de fecha en la nueva pantalla
   # Rellena el campo de fecha en la nueva pantalla (probablemente campo 'Fecha Comprobante')
    try:
        date_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'fc'))
        )
        date_input.clear()  # Asegúrate de limpiar el campo antes de ingresar la fecha
        date_input.send_keys(fecha_comprobante)
    except TimeoutException:
        print("No se pudo encontrar el campo de fecha.")
    except NoSuchElementException as e:
        print(f"Error: {e}")        
        # Selecciona la opción "Servicios"
    try:
        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'idconcepto'))
        )
        select = Select(select_element)
        select.select_by_value('2')  # Selecciona "Servicios"
    except TimeoutException:
        print("No se pudo encontrar el menú de concepto.")
    except NoSuchElementException as e:
        print(f"Error: {e}")
    # Introduce las fechas en los campos correspondientes
    try:
        # Fecha desde
        desde_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'fsd'))
        )
        desde_input.clear()
        desde_input.send_keys(fecha_desde)

        # Fecha hasta
        hasta_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'fsh'))
        )
        hasta_input.clear()
        hasta_input.send_keys(fecha_hasta)

        # Fecha de vencimiento
        vencimiento_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'vencimientopago'))
        )
        vencimiento_input.clear()
        vencimiento_input.send_keys(fecha_expiracion)

# Seleccionar la opción "620900 - SERVICIOS DE INFORMÁTICA N.C.P."

        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'actiAsociadaId'))
        )
        select = Select(select_element)
        select.select_by_value('620900')  # Selecciona la opción por valor
    
# Hacer clic en el botón "Continuar >"
  
        continuar_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='button' and @value='Continuar >']"))
        )
        continuar_button.click()  # Haz clic en el botón
  

# Esperar hasta que el desplegable esté presente

        select_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'idivareceptor'))
        )
        
        # Crear un objeto Select para interactuar con el desplegable
        select = Select(select_element)
        
        # Seleccionar la opción por su valor (en este caso, "5" es el valor para Consumidor Final)
        select.select_by_value('5')

    # Alternativamente, podrías seleccionar la opción por el texto visible:
    # select.select_by_visible_text('Consumidor Final')
    # Esperar hasta que el checkbox esté presente

        checkbox_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'formadepago4'))  # Localizar el checkbox por su ID
        )
        
        # Verificar si el checkbox no está ya seleccionado y hacer clic para seleccionarlo
        if not checkbox_element.is_selected():
            checkbox_element.click()
        
# Esperar hasta que el botón "Continuar" esté presente y hacer clic
 
        continuar_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//input[@type='button' and @value='Continuar >']"))  # Localizar el botón por su atributo 'value'
        )
        continuar_button.click()
        

# Leer la variable de entorno que contiene el valor que deseas ingresar
        #DETALLE_DESCRIPCION = os.getenv('DETALLE_DESCRIPCION', 'Valor por defecto')  # Valor por defecto en caso de que no se defina en .env

# Asegúrate de que el campo textarea esté presente y usa el valor de la variable de entorno para rellenarlo
    
        detalle_textarea = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, 'detalle_descripcion1'))
        )
        detalle_textarea.clear()  # Limpia el campo antes de ingresar el nuevo valor
        detalle_textarea.send_keys(DETALLE_DESCRIPCION)
       
    
        # Espera hasta que el elemento select esté presente en la página
        select_element = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//td/select[@id="detalle_medida1"]'))
        )

        # Usa ActionChains para hacer clic en la lista desplegable
        actions = ActionChains(driver)
        actions.click(select_element).perform()

        # Espera hasta que la opción deseada con el texto "unidades" esté visible y haz clic en ella
        option_to_select = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//td/select[@id="detalle_medida1"]/option[contains(text(), "unidades")]'))
        )
        option_to_select.click()

                # Espera hasta que el campo de texto esté presente en la página
        input_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//input[@id="detalle_precio1"]'))
        )
        
        # Ingresa el valor desde el archivo .env en el campo de texto
        input_element.clear()  # Limpia el campo antes de ingresar el nuevo valor
        input_element.send_keys(detalle_precio)

        continue_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, '//input[@type="button" and @value="Continuar >"]'))
        )

    # Hace clic en el botón "Continuar"
        continue_button.click()

        # Otras acciones...
    
    except TimeoutException:
        print("No se pudo encontrar alguno de los campos de fecha.")
    except NoSuchElementException as e:
        print(f"Error: {e}")

    # Esperar unos segundos para ver los resultados antes de la próxima iteración
    time.sleep(10)

    # Cerrar el navegador después de cada iteración
    driver.quit()