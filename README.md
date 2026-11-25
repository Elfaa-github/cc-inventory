# Inventory Serverless (Track C)

Tugas individu Cloud Computing, Week 12: Design & AWS Setup.

- **Use Case:** Inventory
- **Track:** C (Serverless)
- **Nama:** Zahra Elfatima
- **NIU:** 535709

Proyek ini merupakan implementasi API CRUD sederhana untuk satu entity yaitu **Item**, menggunakan arsitektur serverless di AWS Academy ACF Sandbox.

Klien mengirimkan request melalui **Lambda Function URL**. Request tersebut diproses oleh fungsi **AWS Lambda**, sedangkan data Item disimpan dalam bentuk file JSON di **Amazon S3**.

## Arsitektur

```text
Klien (curl / browser)
   |  HTTPS
   v
Lambda Function URL (auth NONE)
   |
   v
Lambda: inventory-handler (execution role: LabRole)
   |                         |
   v                         v
Bucket S3                CloudWatch Logs
items/{id}.json
```

Seluruh resource dibuat di region **us-east-1** tanpa menggunakan VPC.

Diagram arsitektur tersedia di folder `docs/`, yaitu `CC-PROYEK-INDIVIDU.png` beserta hasil ekspornya.

### Penggantian Layanan dari Contoh Track C

Dua layanan yang digunakan dalam contoh Track C tidak dapat digunakan di AWS Academy Sandbox. Oleh karena itu, kedua layanan tersebut diganti dengan layanan lain yang memiliki fungsi serupa.

| Layanan pada Contoh Track C | Layanan yang Digunakan | Alasan Penggantian |
|---|---|---|
| API Gateway | Lambda Function URL | Pembuatan API melalui API Gateway ditolak oleh Sandbox. Lambda Function URL tetap menyediakan endpoint HTTPS yang dapat digunakan untuk mengakses Lambda. |
| DynamoDB | Amazon S3 | Operasi `CreateTable` pada DynamoDB ditolak oleh Sandbox. S3 digunakan sebagai alternatif untuk menyimpan data Item, dengan setiap Item disimpan dalam satu file JSON. |

## Entity: Item

Proyek ini menggunakan satu entity, yaitu `Item`, dengan atribut sebagai berikut.

| Atribut | Tipe Data | Aturan |
|---|---|---|
| `id` | Teks | Dibuat secara otomatis oleh server menggunakan UUID versi 4. |
| `name` | Teks | Wajib diisi dan tidak boleh kosong. |
| `category` | Teks | Wajib diisi dan tidak boleh kosong. |
| `quantity` | Bilangan bulat | Wajib diisi dengan nilai minimal 0. |
| `location` | Teks | Wajib diisi dan tidak boleh kosong. |
| `updated_at` | Teks (waktu ISO, UTC) | Dibuat secara otomatis oleh server. |

## Endpoint API

API menyediakan empat operasi CRUD untuk mengelola data Item.

| Aksi | Method dan Path | Respons Sukses | Respons Gagal |
|---|---|---|---|
| Create | `POST /items` | 201 | 400 (input tidak valid) |
| Read | `GET /items/{id}` | 200 | 404 |
| Update | `PUT /items/{id}` | 200 | 400, 404 |
| Delete | `DELETE /items/{id}` | 200 | 404 |

Method lain pada path yang sudah dikenal akan menghasilkan respons `405 Method Not Allowed`, sedangkan path yang tidak dikenal akan menghasilkan respons `404 Not Found`.

Seluruh respons API menggunakan format JSON.

## Struktur Repository

Berikut adalah struktur folder proyek:

```text
.
├── README.md
├── src/
│   └── lambda_function.py     # Kode Lambda
├── docs/
│   ├── design-brief.pdf       # Design brief
│   └── CC-PROYEK-INDIVIDU.png  # Diagram arsitektur
│
└── evidence/                  # Tangkapan layar bukti AWS
```

Folder `src/` berisi kode fungsi Lambda, folder `docs/` berisi dokumen perancangan dan diagram arsitektur, sedangkan folder `evidence/` berisi tangkapan layar sebagai bukti implementasi dan pengujian di AWS.

## Deployment Plan

Deployment dilakukan melalui **AWS Academy ACF Sandbox**. Seluruh resource yang dibuat akan terhapus ketika timer lab berakhir. Oleh karena itu, proses deployment dapat diulangi dari awal.

### 1. Memulai Lab

- Buka AWS Academy dan jalankan lab ACF Sandbox hingga statusnya menunjukkan dapat dimulai.
- Buka AWS Console.
- Pastikan region yang digunakan adalah **us-east-1**, karena Sandbox hanya mengizinkan penggunaan region tersebut.

### 2. Membuat Bucket S3

- Buat bucket S3 dengan nama yang unik secara global.
- Nama bucket harus menggunakan huruf kecil, angka, dan tanda hubung, dengan panjang 3–63 karakter.
- Contoh nama bucket: `inventory-<nama>-<tanggal>`.
- Pastikan opsi **Block all public access** tetap aktif agar bucket tidak dapat diakses secara publik.

### 3. Membuat Fungsi Lambda

- Pilih **Author from scratch**.
- Isi nama fungsi dengan `inventory-handler`.
- Pilih runtime Python. Pada pengujian proyek ini digunakan Python 3.13.
- Pada bagian **Additional settings**, aktifkan **Custom execution role** atau pilih **Use an existing role**.
- Pilih role **LabRole**.

LabRole digunakan karena pengaturan IAM di Sandbox hanya dapat dibaca sehingga pembuatan role baru tidak dapat dilakukan.

### 4. Memasang Kode Lambda

- Buka fungsi Lambda yang telah dibuat.
- Tempelkan isi file `src/lambda_function.py` ke editor kode pada AWS Console.
- Pastikan handler menggunakan `lambda_function.lambda_handler`.
- Klik **Deploy** untuk menerapkan perubahan kode.

### 5. Mengatur Environment Variable

- Buka menu **Configuration > Environment variables**.
- Tambahkan environment variable dengan konfigurasi berikut:

| Key | Value |
|---|---|
| `BUCKET_NAME` | Nama bucket S3 yang telah dibuat |

### 6. Membuat Lambda Function URL

- Buka menu **Configuration > Function URL**.
- Pilih **Create function URL**.
- Atur authentication type menjadi **NONE**.
- Buat Function URL dan salin alamat endpoint yang dihasilkan.

Format Function URL:

```text
https://<url-id>.lambda-url.us-east-1.on.aws
```

AWS Console akan membuat resource-based policy secara otomatis. Untuk menggunakan authentication type `NONE`, policy harus mengizinkan kedua action berikut:

- `lambda:InvokeFunctionUrl`
- `lambda:InvokeFunction`

Jika kedua izin tersebut tidak tersedia, pemanggilan Function URL akan menghasilkan respons `403 Forbidden`.

### 7. Melakukan Pengujian API

Pengujian dilakukan menggunakan `curl` melalui AWS CloudShell. Contoh pengujian tersedia pada bagian **Contoh Pengujian API** di bawah.

### 8. Memeriksa CloudWatch Logs

- Buka fungsi Lambda.
- Pilih tab **Monitor**.
- Klik **View CloudWatch logs**.
- Buka log stream terbaru.
- Periksa log yang menampilkan baris `START`, `END`, dan `REPORT`.

## Contoh Pengujian API

Pengujian berikut menggunakan `curl` melalui AWS CloudShell.

Sebelum menjalankan perintah, ganti nilai `URL` dengan alamat Lambda Function URL yang telah dibuat. Pastikan tidak ada garis miring (`/`) di bagian akhir URL.

```bash
URL="https://<url-id>.lambda-url.us-east-1.on.aws"
```

### 1. Create Item (201 Created)

Mengirimkan request untuk membuat Item baru.

```bash
curl -i -X POST "$URL/items" -H "Content-Type: application/json" \
  -d '{"name":"Contoh barang","category":"Contoh","quantity":3,"location":"Gudang A"}'
```

### 2. Read Item (200 OK)

Mengambil data Item berdasarkan ID yang diperoleh dari respons Create.

```bash
curl -i "$URL/items/ID"
```

Ganti `ID` dengan ID Item yang dihasilkan saat proses Create.

### 3. Update Item (200 OK)

Memperbarui data Item berdasarkan ID.

```bash
curl -i -X PUT "$URL/items/ID" -H "Content-Type: application/json" \
  -d '{"name":"Contoh barang","category":"Contoh","quantity":7,"location":"Gudang A"}'
```

### 4. Menguji Input Tidak Valid (400 Bad Request)

Mengirimkan request Create tanpa atribut `category` untuk menguji validasi input.

```bash
curl -i -X POST "$URL/items" -H "Content-Type: application/json" \
  -d '{"name":"Contoh barang","quantity":1,"location":"Gudang A"}'
```

### 5. Delete Item (200 OK)

Menghapus Item berdasarkan ID.

```bash
curl -i -X DELETE "$URL/items/ID"
```

### 6. Read Item Setelah Dihapus (404 Not Found)

Melakukan pengambilan data kembali untuk memastikan Item yang telah dihapus tidak dapat ditemukan.

```bash
curl -i "$URL/items/ID"
```

## Keamanan

Beberapa pengaturan keamanan yang diterapkan dalam proyek ini adalah:

- **Lambda Function URL:** Menggunakan authentication type `NONE`, sehingga siapa pun yang mengetahui alamat endpoint dapat memanggil API. Pengaturan ini merupakan keputusan yang digunakan untuk keperluan pengujian. Risikonya dibatasi karena seluruh resource di Sandbox akan terhapus ketika timer lab berakhir.
- **Amazon S3:** Bucket menggunakan pengaturan **Block Public Access** sehingga akses publik tetap diblokir.
- **IAM Role:** Fungsi Lambda menggunakan `LabRole` karena pembuatan role baru tidak dapat dilakukan di Sandbox.

## Keterbatasan

Implementasi ini memiliki beberapa keterbatasan sebagai konsekuensi dari penggunaan layanan dan konfigurasi di AWS Academy Sandbox.

1. **Pencarian data:** S3 tidak mendukung pencarian data berdasarkan isi file. Oleh karena itu, Item hanya dapat diambil berdasarkan `id`.
2. **Daftar Item:** API tidak menyediakan endpoint untuk mengambil seluruh daftar Item. Endpoint yang tersedia hanya empat operasi sesuai ketentuan tugas.
3. **Operasi Update dan Delete:** Kedua operasi memeriksa keberadaan Item terlebih dahulu sebelum melakukan penulisan atau penghapusan. Kedua langkah tersebut tidak berjalan secara atomik.
4. **Autentikasi:** API belum menerapkan autentikasi sehingga siapa pun yang mengetahui alamat Function URL dapat mengakses endpoint.

## Bukti Implementasi AWS

Folder `evidence/` berisi tangkapan layar yang menunjukkan proses konfigurasi, implementasi, dan pengujian proyek di AWS Academy ACF Sandbox.

Bukti yang disertakan meliputi:

1. Status lab ACF Sandbox yang aktif.
2. Pesan kesalahan saat mencoba membuat resource DynamoDB dan API Gateway di Sandbox.
3. Bucket S3 yang telah dibuat.
4. Kode fungsi Lambda dan konfigurasi execution role `LabRole`.
5. Environment variable `BUCKET_NAME`.
6. Lambda Function URL dan resource-based policy.
7. Hasil pengujian API menggunakan `curl`, meliputi respons `201`, `200`, `200`, `400`, `200`, dan `404`.
8. File JSON Item yang tersimpan di bucket S3.
9. Log eksekusi fungsi Lambda pada CloudWatch.
