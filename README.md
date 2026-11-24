# Sistem Inventory Serverless di AWS

Proyek individu mata kuliah **Cloud Computing – Week 12: Desain dan Penyiapan AWS**.

- **Nama:** Zahra Elfatima
- **NIU:** 535709

## Deskripsi

Sistem inventory sederhana untuk mencatat dan mengelola data barang, meliputi nama, kategori, jumlah stok, dan lokasi penyimpanan.

Sistem dirancang menggunakan **Track C (Serverless)** pada AWS Learner Lab dengan memanfaatkan Amazon API Gateway, AWS Lambda, dan Amazon DynamoDB.

## Arsitektur Sistem

Berikut merupakan rancangan arsitektur sistem yang akan dibangun:

```text
Client (curl/Postman)
        |
        v
API Gateway (HTTP API)
        |
        v
AWS Lambda
        |
        v
Amazon DynamoDB
```

| Komponen | Nama | Fungsi |
|---|---|---|
| Amazon API Gateway (HTTP API) | `inventory-api` | Menerima permintaan dari client dan meneruskannya ke Lambda. |
| AWS Lambda (Python) | `inventory-handler` | Menjalankan logika untuk operasi CRUD. |
| Amazon DynamoDB | `inventory-items` | Menyimpan data barang. |

**Konfigurasi AWS:**
- **Region:** `us-east-1`
- **IAM Role:** `LabRole` (role yang tersedia di AWS Learner Lab).

## Entitas Data: Item

Sistem menggunakan satu entitas, yaitu `Item`, untuk menyimpan informasi barang.

Tabel DynamoDB bernama `inventory-items` menggunakan `id` bertipe String sebagai *partition key*.

| Atribut | Tipe | Keterangan |
|---|---|---|
| `id` | String | ID unik barang yang dibuat otomatis oleh Lambda. |
| `name` | String | Nama barang (wajib diisi). |
| `category` | String | Kategori barang. |
| `quantity` | Number | Jumlah stok barang. |
| `location` | String | Lokasi penyimpanan barang. |
| `updated_at` | String | Waktu terakhir data diperbarui dengan format ISO 8601. |

## Endpoint CRUD

Sistem dirancang menyediakan empat endpoint untuk mengelola data barang melalui operasi CRUD (*Create, Read, Update,* dan *Delete*).

| Operasi | Endpoint | Fungsi |
|---|---|---|
| Create | `POST /items` | Menambahkan barang baru. |
| Read | `GET /items/{id}` | Mengambil data barang berdasarkan ID. |
| Update | `PUT /items/{id}` | Memperbarui data barang berdasarkan ID. |
| Delete | `DELETE /items/{id}` | Menghapus data barang berdasarkan ID. |

## Rencana Deployment

1. Memastikan Amazon API Gateway tersedia di AWS Learner Lab, kemudian membuat tabel DynamoDB `inventory-items`.
2. Membuat fungsi Lambda `inventory-handler` menggunakan role `LabRole`, kemudian mengujinya dengan event contoh.
3. Membuat HTTP API `inventory-api` dengan empat route dan mengintegrasikannya dengan fungsi Lambda.
4. Menguji seluruh endpoint menggunakan `curl` dan menyimpan hasil pengujian sebagai bukti.
5. Menghentikan penggunaan layanan setelah pengujian selesai dan memeriksa sisa budget Learner Lab.

## Status Pengerjaan

- [x] Membuat repositori Git dan README awal.
- [ ] Menyelesaikan design brief.
- [ ] Membuat diagram arsitektur.
- [ ] Membuat tabel DynamoDB.
- [ ] Membuat dan menguji fungsi Lambda.
- [ ] Membuat HTTP API melalui API Gateway.
- [ ] Menguji endpoint dan mendokumentasikan hasil pengujian AWS.

## Referensi

- Amazon Web Services. *Tutorial: Create a CRUD HTTP API with Lambda and DynamoDB*.  
  https://docs.aws.amazon.com/apigateway/latest/developerguide/http-api-dynamo-db.html