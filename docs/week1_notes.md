# 1. Hafta Notları: Proje İskeleti, Video ve ROI

## Bu hafta ne yaptık?

1. Projenin klasör yapısını kurduk.
2. Videodan (veya kameradan) kare kare görüntü okumayı öğrendik.
3. Fareyle park yerlerini işaretleyen bir araç yazdık ve koordinatları JSON'a kaydettik.
4. Kaydedilen park yerlerini videonun her karesine çizdik.

Henüz "dolu/boş" kararı yok. Bu hafta otoparkın çizgilerini boyadık. Görevliyi 3. haftada işe alacağız.

---

## Temel kavramlar

### 1. Video aslında art arda gelen fotoğraflardır
Video bir flipbook (kenarı çevrilince hareket eden defter) gibidir. Her sayfa bir **kare (frame)**, yani normal bir fotoğraftır. Saniyede 25 kare gösterilirse göz bunu hareket olarak algılar (25 FPS).

```python
cap = cv2.VideoCapture("video.mp4")   # defteri aç
ok, frame = cap.read()                # bir sayfa çevir
```
`ok` False dönerse video bitmiştir. `VideoCapture(0)` yazarsan dosya yerine bilgisayarın kamerası açılır.

### 2. Görüntü = sayılardan oluşan bir tablo
OpenCV'de bir görüntü NumPy dizisidir. Boyutu `(yükseklik, genişlik, 3)` şeklindedir. Son boyuttaki 3 değer her pikselin rengini verir.
- **Dikkat:** OpenCV renkleri **BGR** sırasıyla tutar, RGB değil. Bu yüzden `(0, 0, 255)` kırmızıdır.
- Koordinatlarda `(x, y)` → x sağa, y **aşağıya** doğru artar. Sol üst köşe `(0, 0)`'dır.

### 3. ROI (Region of Interest, İlgi Alanı)
Bütün fotoğrafı analiz etmek gereksiz. Bize sadece park yerleri lazım. ROI, "sadece buraya bak" dediğimiz bölgedir. Her park yerini **4 köşe noktasıyla** tanımladık:
```json
{"id": 1, "points": [[74, 174], [176, 174], [176, 366], [74, 366]]}
```
Neden dikdörtgen değil de 4 nokta? Kamera eğik açıdan bakarsa park yerleri yamuk görünür. 4 serbest nokta her şekli kapsar.

Kamera **sabit** olduğu için bu noktaları sadece bir kere seçiyoruz ve dosyaya kaydediyoruz.

### 4. `cv2.polylines`: poligon çizmek
```python
polygon = np.array(points, dtype=np.int32).reshape((-1, 1, 2))
cv2.polylines(img, [polygon], isClosed=True, color=(255,200,0), thickness=2)
```
- `reshape((-1, 1, 2))`: OpenCV noktaları bu biçimde ister. `-1` "kaç tane gerekiyorsa" demektir.
- `isClosed=True`: son noktayı ilk noktaya bağlar, şekil kapanır.

### 5. Fare olayları (mouse callback)
`cv2.setMouseCallback(pencere, fonksiyon)` → pencerede her fare hareketinde senin fonksiyonun çağrılır. Biz sadece `EVENT_LBUTTONDOWN` (sol tık) ile ilgileniyoruz. Her tıklamada bir köşe eklenir, 4 köşe olunca park yeri tamamlanır.

### 6. `cv2.waitKey()`: hem bekler hem tuş okur
- `waitKey(40)` → 40 ms bekler. 25 FPS'lik video için 1000/25 = 40 ms.
- `waitKey(0)` → bir tuşa basılana kadar sonsuza kadar bekler (pause).
- `& 0xFF` → farklı işletim sistemlerinde tuş kodunu doğru okumak için kullanılır.

---

## Dosyalar ne işe yarıyor?

| Dosya | Görevi |
|---|---|
| `src/config.py` | Bütün ayarlar tek yerde (renkler, dosya yolları). Bir rengi değiştirmek istersen sadece burayı düzenlersin. |
| `src/video_source.py` | Video/kamera açma ve kare okuma |
| `src/spots.py` | Park yerlerini kaydet / yükle / çiz / kes |
| `select_spots.py` | Fareyle park yeri seçme aracı |
| `main.py` | Videoyu oynatıp park yerlerini çizen ana program |
| `scripts/make_sample_video.py` | Test için yapay otopark videosu üretir |

`spots.py` içindeki `crop_spot()` fonksiyonunu şimdilik kullanmıyoruz. 3. haftada her park yerini ayrı ayrı analiz ederken lazım olacak.

## Örnek video hakkında
Gerçek bir otopark videon olmadığı için `make_sample_video.py` yapay bir video üretiyor. Videoda 7 park yeri var, arabalar zamanla gelip gidiyor ve ışık yavaşça değişiyor (bulut efekti). Işık değişimini bilerek ekledim, çünkü 5. haftada "dinamik eşik" konusunu tam bu problem üzerinde çalışacağız.

Gerçek bir video bulursan (YouTube'da "parking lot cctv footage" araması iyi sonuç verir):
```bash
python select_spots.py --source data/benim_videom.mp4
python main.py --source data/benim_videom.mp4
```

---

## Kendini test et
1. OpenCV'de `(255, 0, 0)` hangi renktir?
2. Park yerlerini neden her karede yeniden seçmiyoruz?
3. `isClosed=False` yazsaydık ne değişirdi?
4. `waitKey(1)` yazarsak video neden çok hızlı oynar?

<details><summary>Cevaplar</summary>

1. Mavi (BGR sırası).
2. Kamera sabit, park yerleri yer değiştirmiyor. Bir kere seçip JSON'a kaydetmek yeterli.
3. Son kenar çizilmez, yani dördüncü kenar eksik kalır.
4. Her kare arasında sadece 1 ms beklenir. Bilgisayar ne kadar hızlıysa video o kadar hızlı akar.
</details>

## 2. haftada ne yapacağız?
Görüntüyü "temizleyeceğiz": gri tonlama → Gaussian blur → adaptive threshold. Sonuçta arabaların kenarları beyaz, boş asfalt siyah görünen bir maske elde edeceğiz.
