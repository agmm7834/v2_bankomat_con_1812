import os
from datetime import datetime

class Karta:
    """Bank kartasi klassi"""
    def __init__(self, karta_raqam, pin, turi, amal_muddati):
        self.__karta_raqam = karta_raqam
        self.__pin = pin
        self.turi = turi
        self.amal_muddati = amal_muddati
        self.bloklangan = False
        self.pin_urinishlari = 0
        self.kunlik_limit = 5000000
        self.bugungi_sarflangan = 0
    
    def karta_raqamni_olish(self):
        return self.__karta_raqam
    
    def karta_raqamni_yashirish(self):
        return f"{self.__karta_raqam[:4]} **** **** {self.__karta_raqam[-4:]}"
    
    def pin_tekshirish(self, pin):
        if self.bloklangan:
            return False
        
        if self.__pin == pin:
            self.pin_urinishlari = 0
            return True
        
        self.pin_urinishlari += 1
        if self.pin_urinishlari >= 3:
            self.bloklangan = True
        
        return False
    
    def pin_ozgartirish(self, eski_pin, yangi_pin):
        if not self.pin_tekshirish(eski_pin):
            return False, "Eski PIN kod noto'g'ri"
        
        if len(yangi_pin) != 4 or not yangi_pin.isdigit():
            return False, "PIN kod 4 ta raqamdan iborat bo'lishi kerak"
        
        self.__pin = yangi_pin
        return True, "PIN kod muvaffaqiyatli o'zgartirildi"
    
    def kunlik_limitni_tekshirish(self, summa):
        return (self.bugungi_sarflangan + summa) <= self.kunlik_limit
    
    def sarfni_qoshish(self, summa):
        self.bugungi_sarflangan += summa


class Hisob:
    """Bank hisobi klassi"""
    def __init__(self, hisob_raqam, ism, balans=0):
        self.hisob_raqam = hisob_raqam
        self.ism = ism
        self.__balans = balans
        self.tranzaksiyalar = []
        self.kartalar = []
        self.ochilgan_sana = datetime.now()
    
    def karta_qoshish(self, karta):
        self.kartalar.append(karta)
    
    def balansni_olish(self):
        return self.__balans
    
    def pul_olish(self, summa, karta=None):
        if summa <= 0:
            return False, "Noto'g'ri summa kiritildi"
        
        if summa > self.__balans:
            return False, f"Hisobda yetarli mablag' yo'q (Balans: {self.__balans:,} so'm)"
        
        if summa % 10000 != 0:
            return False, "Faqat 10,000 so'mga karrali summa"
        
        if karta and not karta.kunlik_limitni_tekshirish(summa):
            qolgan = karta.kunlik_limit - karta.bugungi_sarflangan
            return False, f"Kunlik limit oshdi (Qolgan: {qolgan:,} so'm)"
        
        if summa > 2000000:
            return False, "Maksimal limit: 2,000,000 so'm"
        
        self.__balans -= summa
        if karta:
            karta.sarfni_qoshish(summa)
        
        self.tranzaksiya_qoshish("Pul olish", -summa, karta)
        return True, f"{summa:,} so'm olindi"
    
    def pul_qoyish(self, summa, karta=None):
        if summa <= 0:
            return False, "Noto'g'ri summa"
        
        if summa > 10000000:
            return False, "Maksimal: 10,000,000 so'm"
        
        self.__balans += summa
        self.tranzaksiya_qoshish("Pul qo'yish", summa, karta)
        return True, f"{summa:,} so'm qo'yildi"
    
    def pul_otkazish(self, qabul_qiluvchi, summa, izoh=""):
        if summa <= 0:
            return False, "Noto'g'ri summa"
        
        if summa > self.__balans:
            return False, "Yetarli mablag' yo'q"
        
        komissiya = int(summa * 0.01)
        umumiy = summa + komissiya
        
        if umumiy > self.__balans:
            return False, f"Komissiya bilan yetarli emas (Jami: {umumiy:,})"
        
        self.__balans -= umumiy
        self.tranzaksiya_qoshish(
            f"O'tkazma → {qabul_qiluvchi[:10]}...", 
            -umumiy, 
            None,
            f"{izoh} (Komissiya: {komissiya:,})"
        )
        return True, f"{summa:,} so'm o'tkazildi (Komissiya: {komissiya:,})"
    
    def tranzaksiya_qoshish(self, tur, summa, karta=None, izoh=""):
        vaqt = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.tranzaksiyalar.append({
            'vaqt': vaqt,
            'tur': tur,
            'summa': summa,
            'balans': self.__balans,
            'karta': karta.karta_raqamni_yashirish() if karta else "N/A",
            'izoh': izoh
        })
    
    def tarixni_olish(self, oxirgi_n=10):
        if not self.tranzaksiyalar:
            return "Tranzaksiyalar mavjud emas"
        
        r = "\n" + "="*80 + "\n"
        r += "TRANZAKSIYALAR TARIXI\n"
        r += "="*80 + "\n"
        
        for t in self.tranzaksiyalar[-oxirgi_n:]:
            summa_str = f"{t['summa']:+,}"
            r += f"{t['vaqt']} | {t['tur']:<20} | {summa_str:>15} | Balans: {t['balans']:,}\n"
            if t['izoh']:
                r += f"  → {t['izoh']}\n"
        
        r += "="*80
        return r
    
    def hisobotni_olish(self):
        jami_kirim = sum(t['summa'] for t in self.tranzaksiyalar if t['summa'] > 0)
        jami_chiqim = sum(abs(t['summa']) for t in self.tranzaksiyalar if t['summa'] < 0)
        
        h = "\n" + "="*80 + "\n"
        h += "HISOB HISOBOTI\n"
        h += "="*80 + "\n"
        h += f"Hisob: {self.hisob_raqam}\n"
        h += f"Egasi: {self.ism}\n"
        h += f"Ochilgan: {self.ochilgan_sana.strftime('%Y-%m-%d')}\n"
        h += f"Balans: {self.__balans:,} so'm\n"
        h += f"\nKirim: {jami_kirim:,} so'm\n"
        h += f"Chiqim: {jami_chiqim:,} so'm\n"
        h += f"Tranzaksiyalar: {len(self.tranzaksiyalar)} ta\n"
        h += f"\nKartalar: {len(self.kartalar)} ta\n"
        
        for i, k in enumerate(self.kartalar, 1):
            status = "🔴 Bloklangan" if k.bloklangan else "🟢 Faol"
            h += f"  {i}. {k.karta_raqamni_yashirish()} ({k.turi}) - {status}\n"
        
        h += "="*80
        return h


class Bankomat:
    """Bankomat tizimi"""
    def __init__(self):
        self.hisoblar = {}
        self.kartalar = {}
        self.joriy_hisob = None
        self.joriy_karta = None
        self.bankomat_balansi = 10000000
        self.demo_yuklash()
    
    def demo_yuklash(self):
        # Hisob 1 - Ali Valiyev
        h1 = Hisob("20208000123456789012", "Ali Valiyev", 1500000)
        k1 = Karta("8600123456789012", "1234", "HUMO", "12/27")
        k1b = Karta("8600987654321098", "5678", "UZCARD", "06/28")
        h1.karta_qoshish(k1)
        h1.karta_qoshish(k1b)
        
        self.hisoblar[h1.hisob_raqam] = h1
        self.kartalar[k1.karta_raqamni_olish()] = (k1, h1)
        self.kartalar[k1b.karta_raqamni_olish()] = (k1b, h1)
        
        # Hisob 2 - Madina Karimova
        h2 = Hisob("20208000987654321098", "Madina Karimova", 2500000)
        k2 = Karta("8600456789012345", "4321", "HUMO", "03/26")
        h2.karta_qoshish(k2)
        
        self.hisoblar[h2.hisob_raqam] = h2
        self.kartalar[k2.karta_raqamni_olish()] = (k2, h2)
        
        # Hisob 3 - Sardor Aliyev
        h3 = Hisob("20208000111222333444", "Sardor Aliyev", 800000)
        k3 = Karta("8600111222333444", "9876", "UZCARD", "09/27")
        h3.karta_qoshish(k3)
        
        self.hisoblar[h3.hisob_raqam] = h3
        self.kartalar[k3.karta_raqamni_olish()] = (k3, h3)
    
    def tozalash(self):
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def kirish(self):
        self.tozalash()
        print("\n" + "="*80)
        print("BANKOMAT TIZIMIGA XUSH KELIBSIZ".center(80))
        print("="*80)
        print("\nQo'llab-quvvatlanadigan: HUMO, UZCARD, VISA, MASTERCARD")
        
        karta_raqam = input("\nKarta raqami (16 raqam): ").strip()
        
        if karta_raqam not in self.kartalar:
            print("\n❌ Karta topilmadi!")
            input("\nDavom etish uchun Enter...")
            return False
        
        karta, hisob = self.kartalar[karta_raqam]
        
        if karta.bloklangan:
            print("\n❌ Karta bloklangan!")
            input("\nDavom etish uchun Enter...")
            return False
        
        urinishlar = 3 - karta.pin_urinishlari
        while urinishlar > 0:
            pin = input(f"\nPIN kod ({urinishlar} urinish): ").strip()
            
            if karta.pin_tekshirish(pin):
                self.joriy_hisob = hisob
                self.joriy_karta = karta
                print(f"\n✅ Xush kelibsiz, {hisob.ism}!")
                print(f"Karta: {karta.karta_raqamni_yashirish()} ({karta.turi})")
                input("\nDavom etish uchun Enter...")
                return True
            
            urinishlar -= 1
            if urinishlar > 0:
                print("❌ Noto'g'ri PIN!")
        
        print("\n❌ Karta bloklandi!")
        input("\nDavom etish uchun Enter...")
        return False
    
    def asosiy_menyu(self):
        while True:
            self.tozalash()
            print("\n" + "="*80)
            print(f"ASOSIY MENYU - {self.joriy_hisob.ism}".center(80))
            print("="*80)
            print(f"Karta: {self.joriy_karta.karta_raqamni_yashirish()} ({self.joriy_karta.turi})")
            print(f"Limit: {self.joriy_karta.bugungi_sarflangan:,} / {self.joriy_karta.kunlik_limit:,} so'm")
            print("="*80)
            print("\n1. Balansni tekshirish")
            print("2. Pul olish")
            print("3. Pul qo'yish")
            print("4. Pul o'tkazish")
            print("5. Tranzaksiyalar tarixi")
            print("6. Hisob hisoboti")
            print("7. PIN kodni o'zgartirish")
            print("8. Chiqish")
            print("\n" + "="*80)
            
            tanlov = input("\nTanlov (1-8): ").strip()
            
            if tanlov == '1':
                self.balans()
            elif tanlov == '2':
                self.pul_olish()
            elif tanlov == '3':
                self.pul_qoyish()
            elif tanlov == '4':
                self.pul_otkazish()
            elif tanlov == '5':
                self.tarix()
            elif tanlov == '6':
                self.hisobot()
            elif tanlov == '7':
                self.pin_ozgartirish()
            elif tanlov == '8':
                self.chiqish()
                break
            else:
                print("\n❌ Noto'g'ri tanlov!")
                input("\nEnter...")
    
    def balans(self):
        self.tozalash()
        print("\n" + "="*80)
        print("BALANS".center(80))
        print("="*80)
        print(f"\nHisob: {self.joriy_hisob.hisob_raqam}")
        print(f"Karta: {self.joriy_karta.karta_raqamni_yashirish()}")
        print(f"\n💰 Balans: {self.joriy_hisob.balansni_olish():,} so'm")
        print(f"\n📊 Kunlik limit: {self.joriy_karta.bugungi_sarflangan:,} / {self.joriy_karta.kunlik_limit:,}")
        print("\n" + "="*80)
        input("\nEnter...")
    
    def pul_olish(self):
        self.tozalash()
        print("\n" + "="*80)
        print("PUL OLISH".center(80))
        print("="*80)
        print(f"\nBalans: {self.joriy_hisob.balansni_olish():,} so'm")
        
        qolgan = self.joriy_karta.kunlik_limit - self.joriy_karta.bugungi_sarflangan
        print(f"Qolgan limit: {qolgan:,} so'm")
        print(f"Bankomat: {self.bankomat_balansi:,} so'm")
        
        print("\n" + "-"*80)
        print("1. 50,000 so'm")
        print("2. 100,000 so'm")
        print("3. 200,000 so'm")
        print("4. 500,000 so'm")
        print("5. 1,000,000 so'm")
        print("6. Boshqa summa")
        print("7. Orqaga")
        
        tanlov = input("\nTanlov: ").strip()
        
        summa_map = {'1': 50000, '2': 100000, '3': 200000, '4': 500000, '5': 1000000}
        
        if tanlov in summa_map:
            summa = summa_map[tanlov]
        elif tanlov == '6':
            try:
                summa = int(input("\nSumma: "))
            except ValueError:
                print("\n❌ Noto'g'ri summa!")
                input("\nEnter...")
                return
        elif tanlov == '7':
            return
        else:
            print("\n❌ Noto'g'ri tanlov!")
            input("\nEnter...")
            return
        
        if summa > self.bankomat_balansi:
            print(f"\n❌ Bankomatda yetarli naqd yo'q (Mavjud: {self.bankomat_balansi:,})")
            input("\nEnter...")
            return
        
        ok, msg = self.joriy_hisob.pul_olish(summa, self.joriy_karta)
        
        if ok:
            self.bankomat_balansi -= summa
            print(f"\n✅ {msg}")
            print(f"Yangi balans: {self.joriy_hisob.balansni_olish():,} so'm")
            print("\n" + "-"*80)
            print(f"Sana: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            print(f"Karta: {self.joriy_karta.karta_raqamni_yashirish()}")
            print(f"Summa: {summa:,} so'm")
            print("-"*80)
        else:
            print(f"\n❌ {msg}")
        
        input("\nEnter...")
    
    def pul_qoyish(self):
        self.tozalash()
        print("\n" + "="*80)
        print("PUL QO'YISH".center(80))
        print("="*80)
        print(f"\nBalans: {self.joriy_hisob.balansni_olish():,} so'm")
        
        try:
            summa = int(input("\nSumma: "))
            
            tasdiq = input(f"\n{summa:,} so'm qo'yishni tasdiqlaysizmi? (h/y): ").lower()
            if tasdiq != 'h':
                print("\n❌ Bekor qilindi")
                input("\nEnter...")
                return
            
            ok, msg = self.joriy_hisob.pul_qoyish(summa, self.joriy_karta)
            
            if ok:
                self.bankomat_balansi += summa
                print(f"\n✅ {msg}")
                print(f"Yangi balans: {self.joriy_hisob.balansni_olish():,} so'm")
            else:
                print(f"\n❌ {msg}")
        except ValueError:
            print("\n❌ Noto'g'ri summa!")
        
        input("\nEnter...")
    
    def pul_otkazish(self):
        self.tozalash()
        print("\n" + "="*80)
        print("PUL O'TKAZISH".center(80))
        print("="*80)
        print(f"\nBalans: {self.joriy_hisob.balansni_olish():,} so'm")
        print("Komissiya: 1%")
        
        qabul = input("\nQabul qiluvchi hisob (20 raqam): ").strip()
        
        if qabul not in self.hisoblar:
            print("\n❌ Hisob topilmadi!")
            input("\nEnter...")
            return
        
        if qabul == self.joriy_hisob.hisob_raqam:
            print("\n❌ O'z hisobingizga o'tkaza olmaysiz!")
            input("\nEnter...")
            return
        
        print(f"Qabul qiluvchi: {self.hisoblar[qabul].ism}")
        
        try:
            summa = int(input("\nSumma: "))
            komissiya = int(summa * 0.01)
            jami = summa + komissiya
            
            print(f"\nSumma: {summa:,} so'm")
            print(f"Komissiya: {komissiya:,} so'm")
            print(f"Jami: {jami:,} so'm")
            
            tasdiq = input(f"\nTaskdiqlaysizmi? (h/y): ").lower()
            if tasdiq != 'h':
                print("\n❌ Bekor qilindi")
                input("\nEnter...")
                return
            
            izoh = input("Izoh: ").strip()
            
            ok, msg = self.joriy_hisob.pul_otkazish(qabul, summa, izoh)
            
            if ok:
                self.hisoblar[qabul].pul_qoyish(summa)
                print(f"\n✅ {msg}")
                print(f"Yangi balans: {self.joriy_hisob.balansni_olish():,} so'm")
            else:
                print(f"\n❌ {msg}")
        except ValueError:
            print("\n❌ Noto'g'ri summa!")
        
        input("\nEnter...")
    
    def tarix(self):
        self.tozalash()
        print(self.joriy_hisob.tarixni_olish(15))
        input("\nEnter...")
    
    def hisobot(self):
        self.tozalash()
        print(self.joriy_hisob.hisobotni_olish())
        input("\nEnter...")
    
    def pin_ozgartirish(self):
        self.tozalash()
        print("\n" + "="*80)
        print("PIN O'ZGARTIRISH".center(80))
        print("="*80)
        
        eski = input("\nEski PIN: ").strip()
        yangi = input("Yangi PIN (4 raqam): ").strip()
        takror = input("Takroriy: ").strip()
        
        if yangi != takror:
            print("\n❌ PIN kodlar mos kelmadi!")
            input("\nEnter...")
            return
        
        ok, msg = self.joriy_karta.pin_ozgartirish(eski, yangi)
        print(f"\n{'✅' if ok else '❌'} {msg}")
        input("\nEnter...")
    
    def chiqish(self):
        self.tozalash()
        print("\n" + "="*80)
        print("XAYR, TASHRIFINGIZ UCHUN RAHMAT!".center(80))
        print("="*80)
        print(f"\nKartangizni oling: {self.joriy_karta.karta_raqamni_yashirish()}")
        self.joriy_hisob = None
        self.joriy_karta = None
    
    def ishga_tushirish(self):
        while True:
            if self.kirish():
                self.asosiy_menyu()
            
            davom = input("\nBoshqa foydalanuvchi? (h/y): ").lower()
            if davom != 'h':
                self.tozalash()
                print("\n" + "="*80)
                print("DASTUR TUGATILDI".center(80))
                print("="*80)
                break


if __name__ == "__main__":
    print("\n" + "="*80)
    print("DEMO HISOBLAR".center(80))
    print("="*80)
    print("\n1. Ali Valiyev")
    print("   Karta: 8600123456789012 | PIN: 1234")
    print("   Balans: 1,500,000 so'm")
    print("\n2. Madina Karimova")
    print("   Karta: 8600456789012345 | PIN: 4321")
    print("   Balans: 2,500,000 so'm")
    print("\n3. Sardor Aliyev")
    print("   Karta: 8600111222333444 | PIN: 9876")
    print("   Balans: 800,000 so'm")
    print("\n" + "="*80)
    input("\nBoshlash uchun Enter...")
    
    atm = Bankomat()
    atm.ishga_tushirish()
  
