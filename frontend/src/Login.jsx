import React, { useEffect, useRef } from "react";
import "./Hero.css";
import { useNavigate } from "react-router-dom";

import hero1 from "../assets/images/home/verdant-hero-1_a441137f.jpg";
import hero2 from "../assets/images/home/verdant-hero-2_b89f14a6.png";
import hero3 from "../assets/images/home/verdant-hero-3_edc4b666.png";
import hero4 from "../assets/images/home/verdant-hero-4_30ae0ca2.png";
import hero5 from "../assets/images/home/verdant-hero-5_4a10167e.png";

import hero6 from "../assets/images/home/verdant-hero-6_97775979.png";

import hero7 from "../assets/images/home/verdant-hero-7_8a593e16.png";
import hero8 from "../assets/images/home/verdant-hero-8_1919eb53.png";
import hero9 from "../assets/images/home/verdant-hero-9_336d218b.png";
import hero10 from "../assets/images/home/verdant-hero-10_7b288a54.png";


import glow1 from "../assets/images/home/verdant-hero-green-1_5c97ead5.png";
import glow2 from "../assets/images/home/verdant-hero-green-2_91937e94.png";
import glow3 from "../assets/images/home/verdant-hero-green-3_cfbc2995.png";
import glow4 from "../assets/images/home/verdant-hero-green-4_49edcd30.png";
import glow5 from "../assets/images/home/verdant-hero-green-5_ff4835dc.png";
import glow6 from "../assets/images/home/verdant-hero-green-6_f3a367a9.png";


const layers = [
    { src: hero1, className: "bg parallax", speed: 50 },
    { src: hero2, className: "layer1 parallax", speed: 10 },
    { src: hero3, className: "layer1 parallax", speed: 80 },
    { src: hero4, className: "layer1 parallax", speed: 20 },
    { src: hero5, className: "layer1 parallax", speed: 15 },
    { src: hero6, className: "layer1 parallax", speed: 10 },
    { src: hero7, className: "layer1 parallax", speed: 80 },
    { src: hero8, className: "layer1 parallax", speed: 50 },
    { src: hero9, className: "layer1 parallax", speed: 50 },
    { src: hero10, className: "layer1 parallax", speed: 7 },

    { src: glow1, className: "glow parallax glow1", speed: 8 },
    { src: glow2, className: "glow" },
    { src: glow3, className: "glow parallax glow2", speed: 12 },
    { src: glow4, className: "glow" },
    { src: glow5, className: "glow parallax glow3", speed: 16 },
    { src: glow6, className: "glow" }
];

function Hero() {
    const navigate = useNavigate();
    const heroRef = useRef(null);
    const words = [
        "HUMANISTS",
        "TECHNOLOGISTS",
        "THINKERS",
        "BUILDERS",
        "INNOVATORS"
    ];

    const [index, setIndex] = React.useState(0);
    const [animate, setAnimate] = React.useState(true);

    useEffect(() => {
        const interval = setInterval(() => {
            setAnimate(false); // trigger exit animation

            setTimeout(() => {
                setIndex((prev) => (prev + 1) % words.length);
                setAnimate(true); // trigger enter animation
            }, 300); // exit duration
        }, 2500);

        return () => clearInterval(interval);
    }, []);

    const text = words[index];


    useEffect(() => {
        const handleMouseMove = (e) => {
            const x = (e.clientX / window.innerWidth - 0.5);
            const y = (e.clientY / window.innerHeight - 0.5);

            const layers = heroRef.current.querySelectorAll(".parallax");

            layers.forEach((layer) => {
                const speed = layer.getAttribute("data-speed");
                const moveX = x * speed;
                const moveY = y * speed;

                layer.style.transform = `translate(${moveX}px, ${moveY}px)`;
            });
        };

        window.addEventListener("mousemove", handleMouseMove);

        return () => window.removeEventListener("mousemove", handleMouseMove);
    }, []);



    return (
        <section className="hero" ref={heroRef}>
            {layers.map((layer, i) => (
                <img
                    key={i}
                    src={layer.src}
                    className={layer.className}
                    data-speed={layer.speed}
                />
            ))}
            <div className="overlay"></div>

            <div className="content">

                <h2 className="dynamic-text">WE ARE</h2>

                <h1 className={`changing-word ${animate ? "enter" : "exit"}`}>
                    {words[index]}
                </h1>
                <p>
                    Multi-agent system combining multiple LLMs to generate the most
                    accurate and refined answers.
                </p>
                {/* <button className="btn">Get Started</button> */}
                <button className="btn" onClick={() => navigate("/chat")}>
                    Get Started
                </button>
            </div>
        </section>
    );
}

export default Hero;