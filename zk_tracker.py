import os
import argparse
from datetime import datetime

#TODO: Descomplejizar el codigo.

# TODO: Make this up into an external file.
# User configuration
BASE_PATH = "/tmp/disk/ARCHIVO/r/estudio/study_support/notes/obsidian/study/"
REVIEW_CONTROL_FILE = "review_control.txt"


class OSManager:
    @staticmethod
    def list_files(directory, extension="",starts=""):
        if extension == "":
            return [f for f in os.listdir(directory) if f.startswith(starts)]
        return [f for f in os.listdir(directory) if f.endswith(extension)]

    @staticmethod
    def read_file(file_name):
        if not os.path.exists(file_name):
            return []
        with open(file_name, "r") as file:
            return file.readlines()

    @staticmethod
    def save_file(file_name, data):
        with open(file_name, "w") as file:
            for item in data:
                file.write(",".join(item) + "\n")


class ZKTracker:
    @staticmethod
    def read_review_file(file_name):
        lines = OSManager.read_file(file_name)
        return [line.strip().split(",") for line in lines]

    @staticmethod
    def save_review_file(review_list, file_name):
        OSManager.save_file(file_name, review_list)

    @staticmethod
    def get_new_files(files_in_directory, reviewed_files):
        return [f for f in files_in_directory if f not in reviewed_files]

    @staticmethod
    def create_session_file_name(session_subject):
        to_name = f"review_file_{session_subject.strip().replace(' ', '_')}_{datetime.now().strftime('%Y-%m-%d')}.txt"
        return to_name

    @staticmethod
    def create_partial_review_list(new_files):
        return [[file, "pendiente", "pendiente", "pendiente", "pendiente", "pendiente"] for file in new_files]

    @staticmethod
    def update_review_status(review_list, file_index, field):
        review_list[file_index][field] = "repasada"
        return review_list


class StudyManager:
    @staticmethod
    def learn():
        reviewed_files = {item[0] for item in ZKTracker.read_review_file(REVIEW_CONTROL_FILE)}
        files_in_directory = OSManager.list_files(BASE_PATH, ".md")
        new_files = ZKTracker.get_new_files(files_in_directory, reviewed_files)

        if (len(new_files) == 0):
            print("No se han encontrado notas nuevas.")
            return;

        session_subject = input("Indica el topico de la sesion de estudio: ")
        session_file_name = ZKTracker.create_session_file_name(session_subject)

        print(f"Se han encontrado {len(new_files)} nuevas Notas.")
        print("Respondiendo a las siguientes preguntas:")

        for new_file in new_files:
            with open(BASE_PATH + new_file, "r") as file:
                lines = file.readlines()
                if lines:
                    print(f"> {lines[-1].strip()}")

        partial_review_list = ZKTracker.create_partial_review_list(new_files)
        control_list = ZKTracker.read_review_file(REVIEW_CONTROL_FILE)
        control_list.extend([[file] for file in new_files])

        ZKTracker.save_review_file(control_list, REVIEW_CONTROL_FILE)
        ZKTracker.save_review_file(partial_review_list, session_file_name)

        print("Proceso de 'learn' completado.")

    @staticmethod
    def reviewed():
        review_files = OSManager.list_files("./", starts="review_file_")

        if not review_files:
            print("No hay archivos de sesión de repaso disponibles.")
            return

        print("Lista de archivos de repaso disponibles:")
        for idx, file in enumerate(review_files, start=1):
            print(f"{idx}. {file}")

        try:
            selected_index = int(input("Selecciona el número del archivo que repasaste: ")) - 1
            if selected_index < 0 or selected_index >= len(review_files):
                print("Índice fuera de rango.")
                return
            selected_file = review_files[selected_index]
            review_list = ZKTracker.read_review_file(selected_file)

            print("Lista de archivos dentro de la sesión de repaso seleccionada:")
            for idx, item in enumerate(review_list, start=1):
                print(f"{idx}. {item[0]}")

            file_index = int(input("Selecciona el número de la nota que repasaste: ")) - 1
            if file_index < 0 or file_index >= len(review_list):
                print("Índice fuera de rango.")
                return

            field = int(input("Ingresa qué revisión hiciste:\n"
                              "1. Al día siguiente\n"
                              "2. A los 2 días\n"
                              "3. A la semana\n"
                              "4. A las dos semanas\n"
                              "5. Al mes\n\n"))
            if field in [1, 2, 3, 4, 5]:
                return field
            else:
                print("Opción no válida. Por favor, ingresa un número entre 1 y 5.")
            return

            review_list = ZKTracker.update_review_status(review_list, file_index, field)
            ZKTracker.save_review_file(review_list, selected_file)
            print(f"El archivo '{review_list[file_index][0]}' ha sido marcado como 'repasada' en el campo {field}.")
        except ValueError:
            print("Valor no válido. Por favor, ingresa un número válido.")

    @staticmethod
    def get_to_day_files(date_aimed):
        files = OSManager.list_files(".", starts="review_file_")

        to_day_files = [file for file in files if date_aimed in file]
        print("Archivos correspondientes al día indicado:")
        for file in to_day_files:
            print(file)

        return to_day_files

    @staticmethod
    def find_items_to_review(files):
        items_review = list()
        for review_file in files:
            if os.path.exists(review_file):
                with open(review_file, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:

                        nombre_nota = line.split(',')[0].strip()
                        file_path = os.path.join(BASE_PATH, nombre_nota)

                        if os.path.exists(file_path):
                            with open(file_path, 'r', encoding='utf-8') as nota_file:
                                nota_lines = nota_file.readlines()
                                if nota_lines:
                                    items_review.append(nota_lines[-1].strip())
                        else:
                            print(f"Archivo de nota no encontrado: {nombre_nota}")
            else:
                print(f"Archivo de repaso no encontrado: {review_file}")
        return items_review

    @staticmethod
    def review_items(items_to_review):
        for item in items_to_review:
            print(f"\nResponde la siguiente pregunta:\n\n> {item}\n\n")
            print("Si no lo recordas, volve a la nota e intenta reconstruir la logica o mnemotecnia. You can do it!\n")
            input("Presiona Enter cuando hayas terminado de repasar esta pregunta.")
        print("Terminaste! Muy bien hecho.")

    @staticmethod
    def review():
        date_aimed = input("Indique la fecha de la sesion de estudio formato yyyy-mm-dd: ")
        files = StudyManager.get_to_day_files(date_aimed)
        if not files:
            print("No hay archivos para el día de hoy.")
            return

        items_to_review = StudyManager.find_items_to_review(files)
        if not items_to_review:
            print("No se encontraron items pendientes.")
            return

        StudyManager.review_items(items_to_review)


def main():
    parser = argparse.ArgumentParser(description="CLI para gestionar notas a repasar.")
    parser.add_argument("command", choices=["learn", "reviewed", "review"], help="Comando a ejecutar")
    args = parser.parse_args()

    if args.command == "learn":
        StudyManager.learn()
    elif args.command == "reviewed":
        StudyManager.reviewed()
    elif args.command == "review":
        StudyManager.review()


if __name__ == "__main__":
    main()
