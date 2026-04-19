.hero {
  position: relative;
  height: 100vh;
  overflow: hidden;
  color: white;
}
.hero::after {
  content: "";
  position: absolute;
  bottom: -1px;
  left: 0;

  width: 100%;
  height: 200px;

  background: linear-gradient(
    to bottom,
    rgba(0,0,0,0),
    rgba(0,0,0,1)
  );

  pointer-events: none;
  z-index: 10;
}

/* Background layers */
/* .hero img {
  position: absolute;
  width: 110%;
  height: 110%;
  object-fit: cover;
  pointer-events: none;
} */

.hero img {
  position: absolute;
  top: 0;
  left: 0;
  width: 110%;   /* 🔥 CHANGE FROM 110% */
  height: 100%;
  object-fit: cover;
  transition: transform 0.2s ease-out;
}

/* Individual layers */
.bg {
  z-index: 1;
}

.layer1 {
  z-index: 2;
  opacity: 1;
    /* 🔥 KEY FIX */
   /* animation: float1 5s ease-in-out infinite;  */
}

.layer2 {
  z-index: 3;
  opacity: 10;
  mix-blend-mode: darken;
  /* animation: float2 14s ease-in-out infinite; */
}

.glow {
  z-index: 4;
  /* opacity: 0.5;
  mix-blend-mode: lighten;
  animation: glowMove 12s ease-in-out infinite; */
    opacity: 0;
  animation: glowBlink 6s infinite;
}

/* Each glow delayed */
.glow1 {
  animation-delay: 0s;
}

.glow2 {
  animation-delay: 10s;
}

.glow3 {
  animation-delay: 15s;
}

.parallax {
  transition: transform 0.1s linear;
}

/* Keyframe */
@keyframes glowBlink {
  0%   { opacity: 0; }
  20%  { opacity: 0.8; }
  40%  { opacity: 0.5; }
  100% { opacity: 0; }
}

/* Overlay */
.overlay {
  position: absolute;
  width: 100%;
  height: 100%;
  background: linear-gradient(
    to right,
    rgba(11, 15, 25, 0.50),
    rgba(11, 15, 25, 0.40)
  );
  z-index: 5;
}

/* Content */
.content {
  position: relative;
  z-index: 10;

  height: 100%;
  width: 100%;

  display: flex;
  flex-direction: column;
  justify-content: center;   /* vertical center */
  align-items: center;       /* horizontal center */

  text-align: center;
}
.content h1 {
  font-size: 64px;
  line-height: 1.1;
  margin-bottom: 20px;
}

/* .content p {
  opacity: 0.8;
  margin-bottom: 30px;
} */
 .content p {
  margin-top: 20px;
  max-width: 600px;
  opacity: 0.7;
}

.content button {
  padding: 14px 30px;
  border-radius: 8px;
  border: none;
  background: linear-gradient(90deg, #3b82f6, #06b6d4);
  color: white;
  cursor: pointer;
}

/* Animations */

.dynamic-text {
    font-family: 'Inter', sans-serif;
  font-size: 18px;
  letter-spacing: 4px;
  margin-bottom: 0px;
  opacity: 0.8;
}

.changing-word {
    margin-top: 0px; 
    font-family: 'Playfair Display', serif;
    display: block;
  font-size: 500px;   /* 🔥 BIG like Verdant */
  font-weight: 500;
  letter-spacing: 6px;
  color: #078a65b5;
  /* text-shadow: 0 0 20px rgba(6, 182, 212, 0.3); */
  animation: fadeText 0.6s ease-in-out;
}

/* ENTER (appear) */
.enter {
  opacity: 1;
  transform: translateY(0px) scale(1);
  filter: blur(0px);
}

/* EXIT (disappear) */
.exit {
  opacity: 0;
  transform: translateY(30px) scale(0.98);
  filter: blur(6px);
}

@keyframes fadeText {
  0% { opacity: 0; transform: translateY(20px); }
  100% { opacity: 1; transform: translateY(0); }
}


@keyframes float1 {
  0% { transform: translateY(0px); }
  50% { transform: translateY(-20px); }
  100% { transform: translateY(0px); }
}

@keyframes float2 {
  0% { transform: translateY(0px); }
  50% { transform: translateY(20px); }
  100% { transform: translateY(0px); }
}

@keyframes glowMove {
  0% { transform: translateX(0px); }
  50% { transform: translateX(30px); }
  100% { transform: translateX(0px); }
}