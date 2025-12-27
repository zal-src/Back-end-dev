const heroBg = document.querySelector('.hero-bg');

const images = [
  'img/pexels-minan1398-1087727.jpg',
  'img/pexels-naimbic-2610815.jpg',
  'img/pexels-fauxels-3182759.jpg',
  'img/man-looking-clothes-full-shot.jpg'
];

let current = 0;
heroBg.style.backgroundImage = `url(${images[current]})`;

setInterval(() => {
  // fade-out + zoom
  heroBg.style.opacity = 0;
  heroBg.style.transform = "scale(1.05)";

  setTimeout(() => {
    // เปลี่ยนภาพ (สุ่มก็ได้ ถ้าต้องการ)
    current = (current + 1) % images.length;
    heroBg.style.backgroundImage = `url(${images[current]})`;

    // fade-in + zoom กลับ
    heroBg.style.opacity = 1;
    heroBg.style.transform = "scale(1.0)";
  }, 1500);

}, 7000); // เปลี่ยนภาพทุก 7 วินาที

// Sticky navbar with background change on scroll
window.addEventListener('scroll', function() {
    const navbar = document.querySelector('.navbar');
    if (window.scrollY > 50) {
        navbar.classList.add('scrolled');
    } else {
        navbar.classList.remove('scrolled');
    }
});

// Mobile menu toggle
const hamburger = document.querySelector('.hamburger');
const mobileMenu = document.querySelector('.mobile-menu');

hamburger.addEventListener('click', function() {
    mobileMenu.classList.toggle('active');
    
    const icon = hamburger.querySelector('i');
    if (mobileMenu.classList.contains('active')) {
        icon.classList.remove('fa-bars');
        icon.classList.add('fa-times');
    } else {
        icon.classList.remove('fa-times');
        icon.classList.add('fa-bars');
    }
});

// Close mobile menu when clicking on a link
const mobileLinks = document.querySelectorAll('.mobile-links a, .mobile-icon');
mobileLinks.forEach(link => {
    link.addEventListener('click', function() {
        mobileMenu.classList.remove('active');
        const icon = hamburger.querySelector('i');
        icon.classList.remove('fa-times');
        icon.classList.add('fa-bars');
    });
});

// Close mobile menu when clicking outside
document.addEventListener('click', function(event) {
    if (!event.target.closest('.navbar') && !event.target.closest('.mobile-menu')) {
        mobileMenu.classList.remove('active');
        const icon = hamburger.querySelector('i');
        icon.classList.remove('fa-times');
        icon.classList.add('fa-bars');
    }
});

// Hero section scroll indicator - RECOMMENDED VERSION
document.querySelector('.scroll-indicator').addEventListener('click', function() {
    // เลื่อนไปยังส่วน Featured Products (ส่วนสินค้าแนะนำ)
    const featuredProducts = document.querySelector('.featured-products');
    if (featuredProducts) {
        // คำนวณตำแหน่งโดยหักลบด้วยความสูงของ navbar
        const navbar = document.querySelector('.navbar');
        const navbarHeight = navbar ? navbar.offsetHeight : 0;
        const targetPosition = featuredProducts.offsetTop - navbarHeight - 20;
        
        window.scrollTo({
            top: targetPosition,
            behavior: 'smooth'
        });
    } else {
        // ถ้าไม่พบส่วน featured products ให้เลื่อนลงมาตรงๆ
        window.scrollTo({
            top: window.innerHeight,
            behavior: 'smooth'
        });
    }
});

// เพิ่มการเลื่อนด้วย keyboard (ลูกศรลง)
document.addEventListener('keydown', function(e) {
    if (e.key === 'ArrowDown') {
        e.preventDefault();
        document.querySelector('.scroll-indicator').click();
    }
});

// Parallax effect
window.addEventListener('scroll', function() {
    const scrolled = window.pageYOffset;
    const heroBg = document.querySelector('.hero-bg');
    heroBg.style.transform = `scale(1.05) translateY(${scrolled * 0.5}px)`;
});

// Category card hover animation
document.querySelectorAll('.category-card').forEach(card => {
    card.addEventListener('mouseenter', function() {
        this.style.transform = 'translateY(-10px)';
    });
    
    card.addEventListener('mouseleave', function() {
        this.style.transform = 'translateY(0)';
    });
});

// Explore button click
document.querySelectorAll('.explore-btn').forEach(button => {
    button.addEventListener('click', function(e) {
        e.preventDefault();
        const categoryName = this.closest('.category-card').querySelector('.category-name').textContent;
        
        console.log(`Navigating to ${categoryName} category`);
        
        this.style.background = '#28a745';
        this.style.borderColor = '#28a745';
        this.textContent = 'Exploring...';
        
        setTimeout(() => {
            this.style.background = '';
            this.style.borderColor = '';
            this.textContent = 'Explore';
        }, 1500);
    });
});

// About section scroll animation
document.addEventListener('DOMContentLoaded', function() {
    const aboutSection = document.querySelector('.about-section');
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.style.opacity = '1';
                entry.target.style.transform = 'translateY(0)';
            }
        });
    }, { threshold: 0.1 });
    
    aboutSection.style.opacity = '0';
    aboutSection.style.transform = 'translateY(30px)';
    aboutSection.style.transition = 'opacity 0.8s ease, transform 0.8s ease';
    
    observer.observe(aboutSection);
});

// Customer review slider
document.addEventListener('DOMContentLoaded', function() {
    const sliderContainer = document.querySelector('.slider-container');
    const reviewCards = document.querySelectorAll('.review-card');
    const dots = document.querySelectorAll('.dot');
    const prevBtn = document.querySelector('.prev-btn');
    const nextBtn = document.querySelector('.next-btn');
    
    let currentIndex = 0;
    const totalSlides = reviewCards.length;
    
    function updateSlider() {
        sliderContainer.style.transform = `translateX(-${currentIndex * 100}%)`;
        reviewCards.forEach((card, index) => card.classList.toggle('active', index === currentIndex));
        dots.forEach((dot, index) => dot.classList.toggle('active', index === currentIndex));
    }
    
    function nextSlide() { currentIndex = (currentIndex + 1) % totalSlides; updateSlider(); }
    function prevSlide() { currentIndex = (currentIndex - 1 + totalSlides) % totalSlides; updateSlider(); }
    
    nextBtn.addEventListener('click', nextSlide);
    prevBtn.addEventListener('click', prevSlide);
    
    dots.forEach(dot => {
        dot.addEventListener('click', function() {
            currentIndex = parseInt(this.getAttribute('data-index'));
            updateSlider();
        });
    });
    
    let slideInterval = setInterval(nextSlide, 6000);
    
    const slider = document.querySelector('.reviews-slider');
    slider.addEventListener('mouseenter', () => clearInterval(slideInterval));
    slider.addEventListener('mouseleave', () => slideInterval = setInterval(nextSlide, 6000));
    
    document.addEventListener('keydown', (e) => {
        if (e.key === 'ArrowLeft') prevSlide();
        if (e.key === 'ArrowRight') nextSlide();
    });
    
    updateSlider();
});

// Special offer countdown
function updateCountdown(elementId, hours, minutes, seconds) {
    const hoursElement = document.getElementById(`${elementId}-hours`);
    const minutesElement = document.getElementById(`${elementId}-minutes`);
    const secondsElement = document.getElementById(`${elementId}-seconds`);
    
    let totalSeconds = hours * 3600 + minutes * 60 + seconds;
    
    function updateTimer() {
        if (totalSeconds <= 0) {
            hoursElement.textContent = '00';
            minutesElement.textContent = '00';
            secondsElement.textContent = '00';
            return;
        }
        
        totalSeconds--;
        const hrs = Math.floor(totalSeconds / 3600);
        const mins = Math.floor((totalSeconds % 3600) / 60);
        const secs = totalSeconds % 60;
        
        hoursElement.textContent = hrs.toString().padStart(2, '0');
        minutesElement.textContent = mins.toString().padStart(2, '0');
        secondsElement.textContent = secs.toString().padStart(2, '0');
    }
    
    updateTimer();
    setInterval(updateTimer, 1000);
}

// Initialize countdowns
document.addEventListener('DOMContentLoaded', function() {
    updateCountdown('banner', 12, 45, 30);
    updateCountdown('offer1', 8, 24, 12);
    updateCountdown('offer2', 5, 18, 45);
    updateCountdown('offer3', 23, 59, 59);
});

// Contact & support FAQ accordion
document.addEventListener('DOMContentLoaded', function() {
    const faqQuestions = document.querySelectorAll('.faq-question');
    
    faqQuestions.forEach(question => {
        question.addEventListener('click', function() {
            const answer = this.nextElementSibling;
            const isActive = this.classList.contains('active');
            
            document.querySelectorAll('.faq-question').forEach(q => q.classList.remove('active'));
            document.querySelectorAll('.faq-answer').forEach(a => a.classList.remove('active'));
            
            if (!isActive) {
                this.classList.add('active');
                answer.classList.add('active');
            }
        });
    });
});

// Footer newsletter
document.addEventListener('DOMContentLoaded', function() {
    const newsletterForm = document.querySelector('.newsletter-form');
    
    newsletterForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const emailInput = this.querySelector('.newsletter-input');
        const submitBtn = this.querySelector('.newsletter-btn');
        
        if (!emailInput.value || !emailInput.value.includes('@')) {
            emailInput.style.border = '1px solid #e74c3c';
            return;
        }
        
        const originalText = submitBtn.textContent;
        submitBtn.textContent = 'Subscribed!';
        submitBtn.style.background = 'linear-gradient(135deg, #2ecc71, #27ae60)';
        emailInput.value = '';
        
        setTimeout(() => {
            submitBtn.textContent = originalText;
            submitBtn.style.background = '';
            emailInput.style.border = '';
        }, 2000);
        
        console.log('Newsletter subscription:', emailInput.value);
    });
});

// ===========================
// ✅ ENHANCED CART FUNCTIONALITY - FIXED VERSION
// ===========================
document.addEventListener('DOMContentLoaded', function() {
    const cartSidebar = document.getElementById('cart-sidebar');
    const cartItemsContainer = document.getElementById('cart-items');
    const cartTotal = document.getElementById('cart-total');
    const closeCartBtn = document.getElementById('close-cart');
    const cartIcon = document.querySelector('.fa-shopping-cart').closest('.icon');
    const cartCount = document.querySelector('.cart-count');
    const checkoutBtn = document.getElementById('checkout-btn');

    // FIX: ตรวจสอบและแก้ไขข้อมูลใน Local Storage
    function getCartFromStorage() {
        try {
            const cartData = localStorage.getItem('cart');
            console.log('Raw cart data from storage:', cartData);
            
            if (!cartData) {
                return [];
            }
            
            const parsed = JSON.parse(cartData);
            
            // ตรวจสอบว่าเป็น array และมีโครงสร้างที่ถูกต้อง
            if (Array.isArray(parsed)) {
                // กรองเฉพาะ items ที่มีโครงสร้างถูกต้อง
                const validCart = parsed.filter(item => 
                    item && 
                    typeof item === 'object' && 
                    item.name && 
                    typeof item.price === 'number' && 
                    typeof item.qty === 'number'
                );
                console.log('Valid cart items:', validCart);
                return validCart;
            } else {
                console.warn('Cart data is not an array, resetting cart');
                return [];
            }
        } catch (error) {
            console.error('Error loading cart from storage:', error);
            // ถ้ามี error ให้ล้างและเริ่มใหม่
            localStorage.removeItem('cart');
            return [];
        }
    }

    let cart = getCartFromStorage();
    console.log('Initial cart:', cart);

    // เปิด/ปิดตะกร้า
    cartIcon.addEventListener('click', () => {
        cartSidebar.classList.add('active');
    });
    
    closeCartBtn.addEventListener('click', () => {
        cartSidebar.classList.remove('active');
    });

    // เพิ่มสินค้าเข้าตะกร้า - FIXED VERSION
    function initializeAddToCartButtons() {
        // ลบ event listener เดิมทั้งหมด
        const newButtons = [];
        document.querySelectorAll('.add-to-cart').forEach(btn => {
            const newBtn = btn.cloneNode(true);
            btn.parentNode.replaceChild(newBtn, btn);
            newButtons.push(newBtn);
        });

        // เพิ่ม event listener ใหม่
        newButtons.forEach(btn => {
            btn.addEventListener('click', function(e) {
                e.preventDefault();
                e.stopPropagation();
                
                const productCard = this.closest('.product-card, .offer-card');
                if (!productCard) {
                    console.error('Product card not found');
                    return;
                }

                const name = productCard.querySelector('.product-name, .offer-title')?.textContent;
                const priceText = productCard.querySelector('.current-price')?.textContent.replace('฿','').replace(',','').trim();
                const price = parseFloat(priceText) || 0;
                
                // ดึง URL รูปภาพจาก background-image
                const imageElement = productCard.querySelector('.product-image, .offer-image');
                let imgSrc = '';
                if (imageElement) {
                    const bgImage = imageElement.style.backgroundImage;
                    if (bgImage && bgImage !== 'none') {
                        imgSrc = bgImage.replace(/url\(['"]?(.*?)['"]?\)/i, '$1');
                    }
                }

                console.log('Adding to cart:', { name, price, imgSrc });

                if (!name || price === 0) {
                    console.error('Invalid product data:', { name, price });
                    return;
                }

                addToCart(name, price, imgSrc);
                
                // แสดงการยืนยัน
                showAddToCartAnimation(this);
            });
        });

        console.log('Initialized', newButtons.length, 'add to cart buttons');
    }

    // ฟังก์ชันเพิ่มสินค้าลงตะกร้า
    function addToCart(name, price, imgSrc) {
        console.log('Current cart before add:', cart);
        console.log('Cart type:', typeof cart, 'Is array:', Array.isArray(cart));
        
        // ตรวจสอบว่า cart เป็น array
        if (!Array.isArray(cart)) {
            console.error('Cart is not an array, resetting...');
            cart = [];
        }

        const existing = cart.find(item => item.name === name);
        
        if(existing) {
            existing.qty += 1;
            console.log('Increased quantity for:', name, 'New qty:', existing.qty);
        } else {
            const newItem = {
                name, 
                price, 
                qty: 1, 
                imgSrc: imgSrc || 'img/default-product.jpg'
            };
            cart.push(newItem);
            console.log('Added new item:', newItem);
        }
        
        updateCart();
        saveCartToLocalStorage();
        cartSidebar.classList.add('active');
    }

    // ฟังก์ชันเพิ่มจำนวนสินค้า
    function increaseQuantity(index) {
        if (cart[index]) {
            cart[index].qty += 1;
            updateCart();
            saveCartToLocalStorage();
        }
    }

    // ฟังก์ชันลดจำนวนสินค้า
    function decreaseQuantity(index) {
        if (cart[index]) {
            if (cart[index].qty > 1) {
                cart[index].qty -= 1;
            } else {
                // ถ้าจำนวนเป็น 1 ให้ลบสินค้าออก
                removeFromCart(index);
                return;
            }
            updateCart();
            saveCartToLocalStorage();
        }
    }

    // ฟังก์ชันลบสินค้าออกจากตะกร้า
    function removeFromCart(index) {
        Swal.fire({
            title: 'ลบสินค้า?',
            text: "คุณต้องการลบสินค้านี้ออกจากตะกร้าหรือไม่?",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#d33',
            cancelButtonColor: '#3085d6',
            confirmButtonText: 'ลบ',
            cancelButtonText: 'ยกเลิก'
        }).then((result) => {
            if (result.isConfirmed) {
                cart.splice(index, 1);
                updateCart();
                saveCartToLocalStorage();
                
                Swal.fire(
                    'ลบแล้ว!',
                    'สินค้าถูกลบออกจากตะกร้าแล้ว',
                    'success'
                );
            }
        });
    }

    // อัปเดตรายการตะกร้า
    function updateCart() {
        console.log('Updating cart with:', cart);
        
        // ตรวจสอบว่า cart เป็น array
        if (!Array.isArray(cart)) {
            console.error('Cart is not an array in updateCart, resetting...');
            cart = [];
        }

        cartItemsContainer.innerHTML = '';
        
        if(cart.length === 0) {
            cartItemsContainer.innerHTML = '<p class="empty-cart">ไม่มีสินค้าในตะกร้า</p>';
            cartTotal.innerText = '฿0.00';
            cartCount.innerText = '0';
            return;
        }

        let total = 0;
        
        cart.forEach((item, index) => {
            // ตรวจสอบว่า item มีโครงสร้างถูกต้อง
            if (!item || typeof item !== 'object') {
                console.warn('Invalid item at index', index, 'skipping...');
                return;
            }

            const itemTotal = (item.price || 0) * (item.qty || 0);
            total += itemTotal;
            
            const itemDiv = document.createElement('div');
            itemDiv.classList.add('cart-item');
            itemDiv.innerHTML = `
                <img src="${item.imgSrc || 'img/default-product.jpg'}" alt="${item.name || 'Unknown Product'}" onerror="this.src='img/default-product.jpg'">
                <div class="cart-item-info">
                    <div class="cart-item-name">${item.name || 'Unknown Product'}</div>
                    <div class="cart-item-details">
                        <div class="cart-item-price">฿${(item.price || 0).toFixed(2)} ต่อชิ้น</div>
                        <div class="cart-item-controls">
                            <button class="quantity-btn decrease-btn" data-index="${index}">-</button>
                            <span class="quantity-display">${item.qty || 0}</span>
                            <button class="quantity-btn increase-btn" data-index="${index}">+</button>
                        </div>
                    </div>
                </div>
                <span class="remove-item" data-index="${index}" title="ลบสินค้า">&times;</span>
            `;
            cartItemsContainer.appendChild(itemDiv);
        });

        cartTotal.innerText = `฿${total.toFixed(2)}`;
        
        // อัปเดตตัวเลขข้างๆตะกร้า
        const totalQty = cart.reduce((sum, item) => sum + (item.qty || 0), 0);
        cartCount.innerText = totalQty;

        // เพิ่ม Event Listeners สำหรับปุ่มควบคุมจำนวน
        document.querySelectorAll('.decrease-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.index);
                decreaseQuantity(index);
            });
        });

        document.querySelectorAll('.increase-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.index);
                increaseQuantity(index);
            });
        });

        document.querySelectorAll('.remove-item').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const index = parseInt(e.target.dataset.index);
                removeFromCart(index);
            });
        });
    }

    // บันทึกตะกร้าลง Local Storage
    function saveCartToLocalStorage() {
        try {
            localStorage.setItem('cart', JSON.stringify(cart));
            console.log('Cart saved to storage:', cart);
        } catch (error) {
            console.error('Error saving cart to storage:', error);
        }
    }

    // แสดงอนิเมชันเมื่อเพิ่มสินค้า
    function showAddToCartAnimation(button) {
        const originalHTML = button.innerHTML;
        const originalBackground = button.style.background;
        
        button.innerHTML = '<i class="fas fa-check"></i> เพิ่มแล้ว';
        button.style.background = '#28a745';
        button.style.color = 'white';
        
        setTimeout(() => {
            button.innerHTML = originalHTML;
            button.style.background = originalBackground;
            button.style.color = '';
        }, 2000);
    }

    // ฟังก์ชันชำระเงิน
    checkoutBtn.addEventListener('click', () => {
        if(cart.length === 0){
            Swal.fire({
                icon: 'warning',
                title: 'ตะกร้าว่าง!',
                text: 'กรุณาเลือกสินค้าก่อนชำระเงิน'
            });
            return;
        }

        const totalAmount = cart.reduce((sum, item) => sum + ((item.price || 0) * (item.qty || 0)), 0);
        const totalItems = cart.reduce((sum, item) => sum + (item.qty || 0), 0);

        const qrCodeImg = 'img/45463.jpg';
        Swal.fire({
            title: 'สรุปคำสั่งซื้อ',
            html: `
                <div style="text-align: left;">
                    <p><strong>จำนวนสินค้า:</strong> ${totalItems} ชิ้น</p>
                    <p><strong>ยอดรวม:</strong> ฿${totalAmount.toFixed(2)}</p>
                    <hr>
                    <p>สแกน QR Code เพื่อชำระเงิน</p>
                    <div style="text-align: center; margin: 15px 0;">
                        <img src="${qrCodeImg}" width="200" height="200" style="border: 1px solid #ddd; border-radius: 8px;" onerror="this.style.display='none'">
                    </div>
                    <p style="color: #666; font-size: 14px; text-align: center;">หลังจากชำระเงินแล้ว กรุณาแจ้งหลักฐานการโอน</p>
                </div>
            `,
            showCloseButton: true,
            confirmButtonText: 'ชำระเงินแล้ว',
            showCancelButton: true,
            cancelButtonText: 'ยกเลิก',
            width: 500
        }).then((result) => {
            if (result.isConfirmed) {
                // ล้างตะกร้าหลังชำระเงิน
                cart = [];
                updateCart();
                saveCartToLocalStorage();
                
                Swal.fire(
                    'สำเร็จ!',
                    'ขอบคุณสำหรับการชำระเงิน เราจะจัดส่งสินค้าให้คุณเร็วๆ นี้',
                    'success'
                );
                
                // ปิดตะกร้า
                cartSidebar.classList.remove('active');
            }
        });
    });

    // ฟังก์ชันล้างตะกร้า (สำหรับ debug)
    function clearCart() {
        cart = [];
        updateCart();
        saveCartToLocalStorage();
        console.log('Cart cleared');
    }

    // โหลดตะกร้าเมื่อเริ่มต้น
    initializeAddToCartButtons();
    updateCart();

    // Debug functions
    window.debugCart = function() {
        console.log('Current cart:', cart);
        console.log('Cart type:', typeof cart, 'Is array:', Array.isArray(cart));
        console.log('Add to cart buttons:', document.querySelectorAll('.add-to-cart').length);
        console.log('Local storage cart:', localStorage.getItem('cart'));
    };

    window.clearCart = clearCart;

    console.log('Cart system initialized successfully');
});

// ล้าง Local Storage ถ้ามีปัญหา (รันคำสั่งนี้ใน console) localStorage.removeItem('cart');

// localStorage.removeItem('cart'); 
// Current cart: []
// Cart type: object Is array: true