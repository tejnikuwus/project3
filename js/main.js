/* ==========================================================================
   Артем | Портфоліо: Мікроконтролери, Мехатроніка & Автоматизація
   Main Script File (Vanilla JS)
   ========================================================================== */

document.addEventListener('DOMContentLoaded', () => {
  initNavbar();
  initTypewriter();
  initProjects();
  initSimulator();
  initContactForm();
  initScrollAnimations();
});

/* --- 1. Navbar & Mobile Menu --- */
function initNavbar() {
  const navbar = document.querySelector('.navbar');
  const mobileToggle = document.querySelector('.mobile-toggle');
  const navMenu = document.querySelector('.nav-menu');
  const navLinks = document.querySelectorAll('.nav-link');

  window.addEventListener('scroll', () => {
    if (window.scrollY > 40) {
      navbar.classList.add('scrolled');
    } else {
      navbar.classList.remove('scrolled');
    }

    // Highlight active link based on scroll position
    let current = '';
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
      const sectionTop = section.offsetTop - 120;
      if (window.scrollY >= sectionTop) {
        current = section.getAttribute('id');
      }
    });

    navLinks.forEach(link => {
      link.classList.remove('active');
      if (link.getAttribute('href') === `#${current}`) {
        link.classList.add('active');
      }
    });
  });

  if (mobileToggle) {
    mobileToggle.addEventListener('click', () => {
      navMenu.classList.toggle('active');
    });
  }

  navLinks.forEach(link => {
    link.addEventListener('click', () => {
      navMenu.classList.remove('active');
    });
  });
}

/* --- 2. Typewriter Effect --- */
function initTypewriter() {
  const element = document.getElementById('typed-text');
  if (!element) return;

  const titles = [
    "Розробка мікроконтролерних систем",
    "Мехатроніка & Робототехніка",
    "Веб-диктофон DictoWeb & DSP Аудіо",
    "12-DOF Шагаючі Роботи-павуки",
    "IoT та Автоматизація пристроїв",
    "Учень 10 класу НВК №141 «ОРТ» м. Києва"
  ];

  let titleIndex = 0;
  let charIndex = 0;
  let isDeleting = false;
  let typingSpeed = 70;

  function type() {
    const currentTitle = titles[titleIndex];

    if (isDeleting) {
      element.textContent = currentTitle.substring(0, charIndex - 1);
      charIndex--;
      typingSpeed = 35;
    } else {
      element.textContent = currentTitle.substring(0, charIndex + 1);
      charIndex++;
      typingSpeed = 75;
    }

    if (!isDeleting && charIndex === currentTitle.length) {
      isDeleting = true;
      typingSpeed = 1800; // Pause at end of text
    } else if (isDeleting && charIndex === 0) {
      isDeleting = false;
      titleIndex = (titleIndex + 1) % titles.length;
      typingSpeed = 400; // Pause before new word
    }

    setTimeout(type, typingSpeed);
  }

  type();
}

/* --- 3. Projects Showcase & Modal System --- */
const projectsData = [
  {
    id: 6,
    title: "DictoWeb — Студійний Веб-диктофон & Аудіоконвертер",
    category: "audio",
    categoryLabel: "Web Audio & DSP",
    description: "Сучасний клієнтський веб-диктофон з апаратним вибором мікрофонів, інтерактивним осцилографом (Web Audio API AnalyserNode 60 FPS) у реальному часі, розширеним плеєром та конвертацією записів у формати MP3 (lamejs), 16-bit PCM WAV, WebM та OGG прямо в браузері без серверної частини.",
    image: "assets/dictoweb.svg",
    tags: ["Web Audio API", "DSP", "AudioContext", "lamejs", "WAV PCM", "Canvas API", "Vanilla JS", "MediaStream"],
    linkUrl: "dictoweb/index.html",
    btnText: "🎙️ Відкрити DictoWeb",
    specs: {
      "Аудіо ядро": "Web Audio API (AudioContext, AnalyserNode, MediaStreamTrack)",
      "Формати експорту": "MP3 (128 / 192 / 320 kbps lamejs), WAV (16-bit PCM RIFF), WebM (Opus), OGG",
      "Візуалізація": "HTML5 Canvas Real-Time Waveform & Oscilloscope 60 FPS",
      "Архітектура": "100% Client-side (Zero-backend, повна конфіденційність аудіо)",
      "Можливості плеєра": "Швидкість 0.75x–2.0x, стрибки ±5с, керування гучністю, перейменування записів"
    },
    codeSnippet: `// Web Audio API: Конвертація AudioBuffer у студійний 16-bit WAV (PCM RIFF)
function audioBufferToWav(buffer) {
  const numChannels = buffer.numberOfChannels;
  const sampleRate = buffer.sampleRate;
  const format = 1; // 1 = PCM
  const bitDepth = 16;
  
  const bytesPerSample = bitDepth / 8;
  const blockAlign = numChannels * bytesPerSample;
  const dataLength = buffer.length * blockAlign;
  const bufferLength = 44 + dataLength;
  
  const arrayBuffer = new ArrayBuffer(bufferLength);
  const view = new DataView(arrayBuffer);
  
  // RIFF chunk descriptor
  writeString(view, 0, 'RIFF');
  view.setUint32(4, 36 + dataLength, true);
  writeString(view, 8, 'WAVE');
  // FMT sub-chunk
  writeString(view, 12, 'fmt ');
  view.setUint32(16, 16, true);
  view.setUint16(20, format, true);
  view.setUint16(22, numChannels, true);
  view.setUint32(24, sampleRate, true);
  view.setUint32(28, sampleRate * blockAlign, true);
  view.setUint16(32, blockAlign, true);
  view.setUint16(34, bitDepth, true);
  // DATA sub-chunk
  writeString(view, 36, 'data');
  view.setUint32(40, dataLength, true);
  
  // Interleave channels & write 16-bit signed PCM
  let offset = 44;
  for (let i = 0; i < buffer.length; i++) {
    for (let ch = 0; ch < numChannels; ch++) {
      let sample = buffer.getChannelData(ch)[i];
      sample = Math.max(-1, Math.min(1, sample));
      view.setInt16(offset, sample < 0 ? sample * 0x8000 : sample * 0x7FFF, true);
      offset += 2;
    }
  }
  return new Blob([view], { type: 'audio/wav' });
}`,
    schemaText: "Аудіо-пайплайн: Мікрофон (getUserMedia) -> MediaStreamSource -> AnalyserNode (Canvas 60 FPS) -> MediaRecorder (Opus) -> In-Memory Decoder -> WAV / MP3 (lamejs) / OGG Exporter."
  },
  {
    id: 1,
    title: "Смарт-теплиця на ESP32 & MQTT",
    category: "iot",
    categoryLabel: "IoT & Автоматизація",
    description: "Автономна система клімат-контролю з датчиками вологості ґрунту, температури DHT22 та автоматичним керуванням насосом через MQTT телеметрію.",
    image: "assets/smart_greenhouse.svg",
    tags: ["ESP32", "FreeRTOS", "MQTT", "C++", "Sensors"],
    specs: {
      MCU: "ESP32-WROOM-32U",
      Protocols: "MQTT, WiFi, I2C, ADC",
      Sensors: "DHT22, Soil Moisture Capacitive v1.2, BH1750",
      Actuators: "Relay Module 5V, DC Submersible Pump, Micro Servo"
    },
    codeSnippet: `// ESP32 Smart Greenhouse Control Loop
#include <WiFi.h>
#include <PubSubClient.h>
#include <DHT.h>

#define SOIL_PIN 34
#define RELAY_PIN 23

DHT dht(4, DHT22);
WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  dht.begin();
}

void loop() {
  float temp = dht.readTemperature();
  int soilRaw = analogRead(SOIL_PIN);
  int soilPercent = map(soilRaw, 3500, 1400, 0, 100);
  
  if (soilPercent < 35) {
    digitalWrite(RELAY_PIN, HIGH); // Start watering
    Serial.println("[AUTOPUMP] Triggered: Soil dry!");
  } else {
    digitalWrite(RELAY_PIN, LOW);
  }
  delay(2000);
}`,
    image: "assets/smart_greenhouse.svg",
    schemaText: "Схема підключення: ESP32 GPIO23 -> Реле 5В (Насос), GPIO4 -> DHT22 Датчик, GPIO34 -> Аналоговий сенсор вологості ґрунту."
  },
  {
    id: 2,
    title: "Автономний Робот-маніпулятор на STM32",
    category: "mechatronics",
    categoryLabel: "Мехатроніка",
    description: "4-осьовий мехатроний робот-маніпулятор з обертовою базою, зворотним зв'язком за допомогою серводвигунів MG996R та PID-регулятором траєкторії.",
    image: "assets/stm32_robot_arm.svg",
    tags: ["STM32", "ARM Cortex-M4", "C/C++", "Kinematics", "PWM"],
    specs: {
      MCU: "STM32F401RE (Nucleo-64)",
      Timers: "TIM2, TIM3 16-bit Hardware PWM",
      Servos: "4x MG996R High-Torque Metal Gear",
      Control: "Inverse Kinematics Algorithm"
    },
    codeSnippet: `// STM32 Inverse Kinematics Servo Drive
#include "stm32f4xx_hal.h"

extern TIM_HandleTypeDef htim2;

void Set_Servo_Angle(uint8_t channel, float angle) {
    uint32_t pulse = (uint32_t)(500 + (angle / 180.0f) * 2000);
    switch(channel) {
        case 1: __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_1, pulse); break;
        case 2: __HAL_TIM_SET_COMPARE(&htim2, TIM_CHANNEL_2, pulse); break;
    }
}

void Compute_Arm_Position(float targetX, float targetY) {
    // Inverse Kinematics Math
    float theta1 = atan2(targetY, targetX);
    Set_Servo_Angle(1, theta1 * 180.0f / M_PI);
}`,
    schemaText: "Схема підключення: STM32 PWM Канали TIM2_CH1..CH4 керують сервоприводами за допомогою імпульсів від 0.5мс до 2.5мс."
  },
  {
    id: 3,
    title: "Розумний Дім на Raspberry Pi & ESP-NOW",
    category: "mcu",
    categoryLabel: "Мікроконтролери",
    description: "Бездротова мережа енергоефективних сенсорних нод на базі ESP8266/ESP32 без використання WiFi роутера, зі збором даних на центральний хаб Raspberry Pi.",
    image: "assets/smart_home_hub.svg",
    tags: ["Raspberry Pi", "ESP-NOW", "Python", "C++", "Low-Power"],
    specs: {
      Hub: "Raspberry Pi 4 Model B (Python Gateway)",
      Nodes: "ESP8266 ESP-12F in Deep Sleep",
      Protocol: "ESP-NOW (2.4GHz Peer-to-Peer Direct MAC)",
      Power: "18650 Li-Ion with TP4056 & Sleep Mode"
    },
    codeSnippet: `// ESP-NOW Deep Sleep Sender Node
#include <esp_now.h>
#include <WiFi.h>

uint8_t broadcastAddress[] = {0x24, 0x0A, 0xC4, 0x9A, 0x58, 0x10};

typedef struct struct_message {
  float temp;
  float humidity;
  float batteryVolts;
} struct_message;

struct_message myData;

void setup() {
  WiFi.mode(WIFI_STA);
  esp_now_init();
  esp_now_register_send_cb(OnDataSent);
  
  // Send Sensor Payload and return to Deep Sleep
  esp_now_send(broadcastAddress, (uint8_t *) &myData, sizeof(myData));
  esp_deep_sleep_start();
}`,
    schemaText: "Топологія мережі: Ноди ESP8266 відправляють пакети за 15мс через ESP-NOW і засинають (Deep Sleep струм < 15мкА)."
  },
  {
    id: 4,
    title: "12-DOF Автономний Робот-павук на Raspberry Pi CM5",
    category: "mechatronics",
    categoryLabel: "Мехатроніка",
    description: "Шагаючий робот-павук (Quadruped / Hexapod) з 12 ступенями свободи, інверсною кінематикою (Inverse Kinematics), керуванням по Wi-Fi/Bluetooth та автоматичним обходом перешкод.",
    image: "assets/spider_robot.svg",
    tags: ["Raspberry Pi", "12-DOF Servos", "Inverse Kinematics", "PCA9685", "C++", "3D Printing"],
    specs: {
      MCU: "Raspberry Pi CM5",
      ServoDriver: "3x PCA9685 16-Ch 12-Bit I2C PWM Controller",
      Actuators: "12x MG996R Metal Gear  Servos",
      Sensors: "HC-SR04 Ultrasonic Sensor + MPU6050 IMU Gyro",
      Power: "Li-ion 12v 5V 5A DC-DC Buck Converter",
      GaitEngine: "Tripod & Wave Gait IK Engine (C++)"
    },
    codeSnippet: `secret`,
  },
  {
    id: 5,
    title: "Поліноміальна Регресія та Аналіз Перенавчання (California Housing ML)",
    category: "ml",
    categoryLabel: "Machine Learning & Wasm",
    description: "Інтерактивне дослідження лінійної та поліноміальної регресії: вибір ступеня моделей (повзунки), аналітичні формули ŷ = b₀ + b₁x + ... + bₖxᵏ, порівняння Train/Test MSE та аналіз перенавчання (Overfitting) у середовищі Streamlit stlite.",
    image: "assets/housing_ml.svg",
    tags: ["Python", "scikit-learn", "Polynomial Regression", "Overfitting", "Streamlit", "stlite Wasm"],
    linkUrl: "python/p1.html",
    btnText: "🚀 Відкрити Streamlit (stlite)",
    specs: {
      "Моделі": "Лінійна (ступінь 1) та Поліноміальна (ступінь k)",
      "Формула": "ŷ = b₀ + b₁x + b₂x² + ... + bₖxᵏ",
      "Ознака / Ціль": "MedInc (дохід) → MedHouseValue (вартість житла)",
      "Оцінка": "Окремий розрахунок Train MSE та Test MSE",
      "Платформа": "Streamlit у Pyodide Wasm (без серверу)"
    },
    codeSnippet: `# Поліноміальна регресія та оцінка перенавчання
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error

poly = PolynomialFeatures(degree=k, include_bias=False)
X_train_poly = poly.fit_transform(X_train)
X_test_poly = poly.transform(X_test)

model = LinearRegression().fit(X_train_poly, y_train)
train_mse = mean_squared_error(y_train, model.predict(X_train_poly))
test_mse = mean_squared_error(y_test, model.predict(X_test_poly))`,
    schemaText: "Обидві моделі навчаються виключно на Train вибірці та оцінюються на однакових тестових спостереженнях для об'єктивного виявлення перенавчання."
  }
];

function initProjects() {
  const container = document.getElementById('projects-container');
  const filterBtns = document.querySelectorAll('.filter-btn');
  const modalOverlay = document.getElementById('project-modal');
  const modalClose = document.getElementById('modal-close');
  const modalBody = document.getElementById('modal-body-content');

  if (!container) return;

  function renderProjects(filter = 'all') {
    container.innerHTML = '';
    const filtered = filter === 'all'
      ? projectsData
      : projectsData.filter(p => p.category === filter);

    filtered.forEach(p => {
      const card = document.createElement('div');
      card.className = 'project-card';
      const demoBtnHtml = p.linkUrl
        ? `<a href="${p.linkUrl}" target="_blank" class="btn btn-primary btn-sm" style="margin-right: 8px;">
            ${p.btnText || '🚀 Запустити проект'}
           </a>`
        : '';

      card.innerHTML = `
        <div class="project-image">
          <img src="${p.image}" alt="${p.title}" style="width: 100%; height: 100%; object-fit: cover;">
          <span class="project-badge">${p.categoryLabel}</span>
        </div>
        <div class="project-content">
          <h3 class="project-title">${p.title}</h3>
          <p class="project-desc">${p.description}</p>
          <div class="project-tags">
            ${p.tags.map(t => `<span class="tag">${t}</span>`).join('')}
          </div>
          <div class="project-footer" style="display: flex; gap: 8px; flex-wrap: wrap; margin-top: 16px;">
            ${demoBtnHtml}
            <button class="btn btn-secondary btn-sm open-modal-btn" data-id="${p.id}">
              Детальніше & Specs
            </button>
          </div>
        </div>
      `;
      container.appendChild(card);
    });

    // Attach click listener for modals
    document.querySelectorAll('.open-modal-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const id = parseInt(e.currentTarget.getAttribute('data-id'));
        openProjectModal(id);
      });
    });
  }

  filterBtns.forEach(btn => {
    btn.addEventListener('click', () => {
      filterBtns.forEach(b => b.classList.remove('active'));
      btn.classList.add('active');
      const filter = btn.getAttribute('data-filter');
      renderProjects(filter);
    });
  });

  function openProjectModal(id) {
    const project = projectsData.find(p => p.id === id);
    if (!project) return;

    modalBody.innerHTML = `
      <h2 style="font-size: 1.6rem; margin-bottom: 12px;" class="gradient-text">${project.title}</h2>
      <p style="color: var(--text-muted); margin-bottom: 24px;">${project.description}</p>
      
      <div class="modal-tabs">
        <button class="tab-btn active" data-tab="specs">Специфікація & Компоненти</button>
        <button class="tab-btn" data-tab="code">Код (Source Code)</button>
        <button class="tab-btn" data-tab="schema">Схема</button>
      </div>

      <div class="tab-content" id="tab-specs">
        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 20px;">
          ${Object.entries(project.specs).map(([key, val]) => `
            <div style="background: rgba(0,0,0,0.3); padding: 12px; border-radius: 8px; border: 1px solid var(--border-subtle);">
              <div style="font-family: var(--font-mono); font-size: 0.75rem; color: var(--accent-cyan);">${key}</div>
              <div style="font-size: 0.9rem; font-weight: 600; color: var(--text-main); margin-top: 4px;">${val}</div>
            </div>
          `).join('')}
        </div>
      </div>

      <div class="tab-content" id="tab-code" style="display: none;">
        <pre class="code-block"><code>${escapeHtml(project.codeSnippet)}</code></pre>
      </div>

      <div class="tab-content" id="tab-schema" style="display: none;">
        <div style="background: rgba(0,242,254,0.05); padding: 20px; border-radius: 8px; border: 1px solid var(--border-subtle); color: var(--text-main);">
          <p>🔧 <strong>Схема та електричні зв'язки:</strong></p>
          <p style="margin-top: 10px; color: var(--text-muted);">${project.schemaText}</p>
        </div>
      </div>
    `;

    // Tab switcher logic inside modal
    const tabBtns = modalBody.querySelectorAll('.tab-btn');
    tabBtns.forEach(tBtn => {
      tBtn.addEventListener('click', () => {
        tabBtns.forEach(b => b.classList.remove('active'));
        tBtn.classList.add('active');
        const target = tBtn.getAttribute('data-tab');

        modalBody.querySelectorAll('.tab-content').forEach(tc => {
          tc.style.display = tc.id === `tab-${target}` ? 'block' : 'none';
        });
      });
    });

    modalOverlay.classList.add('active');
  }

  if (modalClose) {
    modalClose.addEventListener('click', () => modalOverlay.classList.remove('active'));
  }

  if (modalOverlay) {
    modalOverlay.addEventListener('click', (e) => {
      if (e.target === modalOverlay) modalOverlay.classList.remove('active');
    });
  }

  renderProjects('all');
}

/* Helper to escape html tags inside code snippet modal */
function escapeHtml(str) {
  return str.replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;");
}

/* --- 4. Interactive MCU Circuit Simulator --- */
function initSimulator() {
  const ledToggle = document.getElementById('sim-led-toggle');
  const ledVisual = document.getElementById('sim-virtual-led');
  const ledStatusText = document.getElementById('sim-led-status');

  const tempSlider = document.getElementById('sim-temp-slider');
  const tempVal = document.getElementById('sim-temp-val');

  const potSlider = document.getElementById('sim-pot-slider');
  const potVal = document.getElementById('sim-pot-val');
  const potVoltage = document.getElementById('sim-pot-voltage');

  const terminalBody = document.getElementById('sim-terminal-body');
  const clearTermBtn = document.getElementById('sim-clear-term');

  if (!ledToggle || !terminalBody) return;

  function appendLog(message, type = 'info') {
    const now = new Date();
    const timeStr = now.toTimeString().split(' ')[0] + '.' + String(now.getMilliseconds()).padStart(3, '0');

    const line = document.createElement('div');
    line.className = 'log-line';
    line.innerHTML = `
      <span class="log-time">[${timeStr}]</span>
      <span class="log-${type}">${message}</span>
    `;
    terminalBody.appendChild(line);
    terminalBody.scrollTop = terminalBody.scrollHeight;
  }

  // Initial welcome log
  appendLog("ESP32-WROOM-32 Booting v1.0.4...", "success");
  appendLog("UART Serial initialized at 115200 baud.", "info");
  appendLog("GPIO 2 (LED), GPIO 4 (DHT22), ADC34 (Potentiometer) READY.", "info");

  // LED Toggle Listener
  ledToggle.addEventListener('click', () => {
    const isCurrentlyOn = ledToggle.classList.contains('on');
    if (isCurrentlyOn) {
      ledToggle.classList.remove('on');
      ledVisual.classList.remove('active');
      ledStatusText.textContent = "LOW (OFF)";
      appendLog("digitalWrite(2, LOW) -> LED OFF", "warn");
    } else {
      ledToggle.classList.add('on');
      ledVisual.classList.add('active');
      ledStatusText.textContent = "HIGH (ON)";
      appendLog("digitalWrite(2, HIGH) -> LED ON", "success");
    }
  });

  // Temperature Slider Listener
  if (tempSlider) {
    tempSlider.addEventListener('input', (e) => {
      const val = parseFloat(e.target.value).toFixed(1);
      tempVal.textContent = `${val} °C`;
      appendLog(`[DHT22] Temperature Sensor Read: ${val} °C`, "info");
    });
  }

  // Potentiometer ADC Slider Listener
  if (potSlider) {
    potSlider.addEventListener('input', (e) => {
      const rawADC = parseInt(e.target.value);
      const voltage = ((rawADC / 4095) * 3.3).toFixed(2);
      potVal.textContent = rawADC;
      potVoltage.textContent = `${voltage}V`;
      appendLog(`[ADC1_CH6] GPIO 34 Raw: ${rawADC} | Voltage: ${voltage}V`, "info");
    });
  }

  // Clear Terminal
  if (clearTermBtn) {
    clearTermBtn.addEventListener('click', () => {
      terminalBody.innerHTML = '';
      appendLog("Serial log cleared.", "info");
    });
  }
}

/* --- 5. Contact Form Handler --- */
function initContactForm() {
  const form = document.getElementById('contact-form');
  const status = document.getElementById('form-status');

  if (!form) return;

  form.addEventListener('submit', (e) => {
    e.preventDefault();

    const name = document.getElementById('form-name').value.trim();
    const email = document.getElementById('form-email').value.trim();
    const message = document.getElementById('form-message').value.trim();

    if (!name || !email || !message) {
      alert("Будь ласка, заповніть усі поля форми.");
      return;
    }

    status.classList.add('success');
    status.style.display = 'block';
    status.textContent = `Дякуємо, ${name}! Ваше повідомлення успішно надіслано Артему.`;

    form.reset();

    setTimeout(() => {
      status.style.display = 'none';
    }, 6000);
  });
}

/* --- 6. Scroll Animations --- */
function initScrollAnimations() {
  const observerOptions = {
    threshold: 0.15
  };

  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('animate-in');

        // If intersecting skills section, trigger skill bar progress width
        if (entry.target.classList.contains('skills-grid')) {
          document.querySelectorAll('.skill-progress').forEach(bar => {
            const level = bar.getAttribute('data-level');
            bar.style.width = `${level}%`;
          });
        }
      }
    });
  }, observerOptions);

  document.querySelectorAll('.section, .skills-grid').forEach(el => {
    observer.observe(el);
  });
}
