# 🧾 Avro to DTO Generator

This web application converts Avro schemas (.avsc) into Java DTO (Data Transfer Object) classes. The generated `.java` file can be downloaded directly from the browser.

**[🔗 Access the application](https://avro-dto-generator.onrender.com)**

## ⚙️ Technologies Used

### 💻 Backend
- **Python 3**
- **Flask** — for serving API endpoints and handling file uploads
- Custom script (`avro_to_dto.py`) to parse Avro schemas and generate Java code

### 🌐 Frontend
- **HTML5**
- **Bootstrap 5** — for a clean, responsive, and professional UI
- **JavaScript** — to handle form submissions and file downloads
- **Dark Mode Support** — toggle between light and dark modes
- **Internationalization** — support for English and Portuguese

## 🔍 Features

- Converts Avro types to appropriate Java types
- Supports nested records and enumerations
- Generates getters and setters
- Generates constructors
- Supports complex types (arrays, maps, etc.)
- Properly handles logical types (timestamp, date, etc.)

## 🚀 How to Run Locally

### Prerequisites
- Python 3.x installed

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

### Step 2: Clone the Repository

```bash
git clone https://github.com/Alerson/avro_dto_webapp.git
cd avro_dto_webapp
```

### Step 3: Install Dependencies

```bash
pip3 install -r requirements.txt
```

### Step 4: Run the Application

```bash
python3 app.py
```

Visit `http://127.0.0.1:5000/` in your browser.

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
├── requirements.txt       # Project dependencies
└── static/                # (Optional) for future CSS/JS
```

## 📥 How It Works

1. The user uploads a `.avsc` file through the browser.
2. The Flask backend saves the file, reads the schema, and generates a Java DTO class using `avro_to_dto.py`.
3. The generated `.java` file is sent back to the browser for download.

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

## 🌐 Hosting

The application is hosted on [Render](https://render.com/) using their free tier. Note that free instances spin down after periods of inactivity, which may cause an initial delay when you access the application.

## 📌 Future Improvements

- [ ] Add live preview of generated Java code
- [ ] Improve file upload UI with drag & drop
- [ ] Add support for downloading a ZIP of multiple DTOs
- [ ] Improve handling of Avro logical types
- [ ] Add automated tests

## 🤝 Contributions

Contributions are welcome!

---

Developed by [Alerson Rigo](mailto:alerson.rigo@gmail.com) | [GitHub](https://github.com/Alerson)