# 🧾 Avro to DTO Generator Web App

This web application allows users to upload an **Avro Schema (.avsc)** file and instantly generate a corresponding **Java DTO (Data Transfer Object)** class. The generated `.java` file can be downloaded directly from the browser.

---

## ⚙️ Technologies Used

### 💻 Backend
- **Python 3**
- **Flask** — for serving the API endpoints and handling file uploads
- Custom script (`avro_to_dto.py`) to parse Avro schemas and generate Java code

### 🌐 Frontend
- **HTML5**
- **Bootstrap 5** — for a clean, responsive, and professional UI
- **Vanilla JavaScript** — to handle form submissions and file downloads

---

## 🚀 How to Run the App

### Step 1: Install Python (if not already installed)

On macOS, it's easiest to use **Homebrew**:

```bash
brew install python
```

Then verify:

```bash
python3 --version
pip3 --version
```

---

### Step 2: Install Required Python Packages

Navigate to the project folder:

```bash
cd avro_dto_webapp
```

Then install Flask:

```bash
pip3 install flask
```

---

### Step 3: Run the Application

From the project directory, run:

```bash
python3 app.py
```

Visit `http://127.0.0.1:5000/` in your browser.

---

## 📁 Project Structure

```
avro_dto_webapp/
│
├── app.py                 # Flask web server
├── avro_to_dto.py         # DTO generator logic
├── templates/
│   └── index.html         # Bootstrap-based frontend
├── uploads/               # Temporarily stores uploaded files
├── output_dto/            # Stores generated Java DTO files
└── static/                # (Optional) for future CSS/JS
```

---

## 📥 How It Works

1. The user uploads a `.avsc` file through the browser.
2. The Flask backend saves the file, reads the schema, and generates a Java DTO class using `avro_to_dto.py`.
3. The generated `.java` file is sent back to the browser for download.

---

## ✅ Example Output

If you upload a file called `user.avsc`, you'll receive:

```
UserDTO.java
```

Containing:
- Fields mapped from Avro types
- Java getters and setters
- Constructor
- Nested classes for records and enums

---

## 🔒 Notes

- Files are saved in temporary folders (`uploads/` and `output_dto/`) which can be cleaned up automatically later.
- Backend only accepts `.avsc` files and returns `.java` files.

---

## 📌 To Do (Optional Enhancements)

- [ ] Add live preview of generated Java code
- [ ] Improve file upload UI with drag & drop
- [ ] Add support for downloading a ZIP of multiple DTOs
- [ ] Dockerize the app for easier deployment

---

Feel free to modify and improve this project to better suit your needs!