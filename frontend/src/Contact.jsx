import "./Footer.css";
import logo from "../assets/images/common/synapsex-logo.png";
// import logo from "../assets/logo.png"; // your SynapseX logo

function Footer() {
  return (
    <footer className="footer">

      {/* Top glow line */}
      <div className="footer-line"></div>

      {/* Logo */}
      <img src={logo} alt="SynapseX Logo" className="footer-logo" />

      {/* Navigation */}
      <div className="footer-links">
        <a href="/about">ABOUT</a>
        <a href="/contact">CONTACT</a>
      </div>

      {/* Bottom text */}
      <p className="footer-copy">
        © 2026 SynapseX. All rights reserved.
      </p>

    </footer>
  );
}

export default Footer;