import React from "react";
import "./Footer.css";

function Footer() {
  return (
    <div className="main-footer">
      &copy;{new Date().getFullYear()} Nanuda | All rights reserved | Made in 🇨🇦
      with ❤️ |{" "}
      <a href="https://github.com/geooff/nanuda" target="_blank">
        View on Github
      </a>
    </div>
  );
}

export default Footer;
