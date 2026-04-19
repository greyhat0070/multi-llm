.footer {
  background: black;
  color: white;

  text-align: center;
  padding: 60px 20px;

  position: relative;
}

/* Glow line */
.footer-line {
  width: 100%;
  height: 1px;

  background: linear-gradient(
    to right,
    transparent,
    #00ffd0,
    transparent
  );

  margin-bottom: 40px;
}

/* Logo */
.footer-logo {
  width: 120px;
  margin-bottom: 20px;

  opacity: 0.9;
}

/* Links */
.footer-links {
  margin-bottom: 20px;
}

.footer-links a {
  margin: 0 15px;
  color: rgba(255,255,255,0.7);
  text-decoration: none;
  letter-spacing: 2px;
  font-size: 14px;

  transition: 0.3s;
}

.footer-links a:hover {
  color: #00ffd0;
}

/* Copyright */
.footer-copy {
  font-size: 12px;
  opacity: 0.5;
}