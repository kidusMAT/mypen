/**
 * Mypen - Dynamic Shooting Stars & Sparks Background
 * Creates a premium canvas animation with drifting particles and shooting stars.
 */

document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.getElementById("star-sparks-bg");
    if (!canvas) return;

    const ctx = canvas.getContext("2d");
    
    // Config
    const starsConfig = {
        count: 100,
        minRadius: 0.5,
        maxRadius: 2.5,
        color: "rgba(212, 140, 17, 0.4)", // Mypen Brand Gold with some opacity
    };

    const shootingStarConfig = {
        minSpeed: 10,
        maxSpeed: 30,
        minDelay: 2000,
        maxDelay: 6000,
        starColor: "#ffffff",
        trailColor: "rgba(212, 140, 17, 0.8)", // Gold trail
        trailLength: 60,
        starWidth: 2,
        starLength: 10
    };

    let width, height;
    let stars = [];
    let shootingStar = null;
    let shootingStarTimeout = null;

    function init() {
        resize();
        window.addEventListener("resize", resize);
        createStars();
        scheduleShootingStar();
        requestAnimationFrame(render);
    }

    function resize() {
        width = window.innerWidth;
        height = window.innerHeight;
        // Retina display support
        const dpr = window.devicePixelRatio || 1;
        canvas.width = width * dpr;
        canvas.height = height * dpr;
        ctx.scale(dpr, dpr);
    }

    // --- Twinkling Stars / Sparks ---
    function createStars() {
        stars = [];
        for (let i = 0; i < starsConfig.count; i++) {
            stars.push({
                x: Math.random() * width,
                y: Math.random() * height,
                radius: Math.random() * (starsConfig.maxRadius - starsConfig.minRadius) + starsConfig.minRadius,
                alpha: Math.random(),
                dAlpha: (Math.random() * 0.02) + 0.005, // twinkling speed
                dx: (Math.random() - 0.5) * 0.2, // slow drift
                dy: (Math.random() - 0.5) * 0.2,
                colorBase: Math.random() > 0.5 ? "212, 140, 17" : "255, 255, 255" // Mix gold and white
            });
        }
    }

    function updateStars() {
        for (let star of stars) {
            // Drift
            star.x += star.dx;
            star.y += star.dy;

            // Wrap around
            if (star.x < 0) star.x = width;
            if (star.x > width) star.x = 0;
            if (star.y < 0) star.y = height;
            if (star.y > height) star.y = 0;

            // Twinkle
            star.alpha += star.dAlpha;
            if (star.alpha > 1 || star.alpha < 0) {
                star.dAlpha = -star.dAlpha;
                star.alpha = Math.max(0, Math.min(1, star.alpha));
            }
        }
    }

    function drawStars() {
        for (let star of stars) {
            ctx.beginPath();
            ctx.arc(star.x, star.y, star.radius, 0, Math.PI * 2);
            // Add subtle glow
            ctx.shadowBlur = 4;
            ctx.shadowColor = `rgba(${star.colorBase}, ${star.alpha})`;
            ctx.fillStyle = `rgba(${star.colorBase}, ${star.alpha})`;
            ctx.fill();
            ctx.shadowBlur = 0;
        }
    }

    // --- Shooting Stars ---
    function spawnShootingStar() {
        const speed = Math.random() * (shootingStarConfig.maxSpeed - shootingStarConfig.minSpeed) + shootingStarConfig.minSpeed;
        const angle = Math.PI / 4 + (Math.random() * 0.2 - 0.1); // ~45 degrees with slight variance
        
        // Start out of bounds
        const startX = Math.random() * width * 1.5;
        const startY = -50;

        shootingStar = {
            x: startX,
            y: startY,
            speed: speed,
            angle: angle,
            length: (Math.random() * 20) + shootingStarConfig.trailLength,
            active: true
        };
    }

    function scheduleShootingStar() {
        clearTimeout(shootingStarTimeout);
        const delay = Math.random() * (shootingStarConfig.maxDelay - shootingStarConfig.minDelay) + shootingStarConfig.minDelay;
        shootingStarTimeout = setTimeout(() => {
            if (!shootingStar || !shootingStar.active) {
                spawnShootingStar();
            }
            scheduleShootingStar();
        }, delay);
    }

    function updateShootingStar() {
        if (!shootingStar || !shootingStar.active) return;
        
        shootingStar.x -= Math.cos(shootingStar.angle) * shootingStar.speed; // moving left-down
        shootingStar.y += Math.sin(shootingStar.angle) * shootingStar.speed;

        // Check bounds
        if (
            shootingStar.x < -100 || 
            shootingStar.y > height + 100
        ) {
            shootingStar.active = false;
        }
    }

    function drawShootingStar() {
        if (!shootingStar || !shootingStar.active) return;

        const tailX = shootingStar.x + Math.cos(shootingStar.angle) * shootingStar.length;
        const tailY = shootingStar.y - Math.sin(shootingStar.angle) * shootingStar.length;

        // Draw trail
        const gradient = ctx.createLinearGradient(shootingStar.x, shootingStar.y, tailX, tailY);
        gradient.addColorStop(0, shootingStarConfig.starColor);
        gradient.addColorStop(0.2, shootingStarConfig.trailColor);
        gradient.addColorStop(1, "transparent");

        ctx.beginPath();
        ctx.strokeStyle = gradient;
        ctx.lineWidth = shootingStarConfig.starWidth;
        ctx.lineCap = "round";
        ctx.moveTo(shootingStar.x, shootingStar.y);
        ctx.lineTo(tailX, tailY);
        // Subtle glow for the shooting star
        ctx.shadowBlur = 10;
        ctx.shadowColor = shootingStarConfig.starColor;
        ctx.stroke();
        ctx.shadowBlur = 0;
    }

    // --- Main Loop ---
    function render() {
        // Clear canvas with transparency (let CSS background show through)
        ctx.clearRect(0, 0, width, height);

        // Optional: draw a subtle radial gradient overlay for depth 
        // similar to the reference site's background
        const bgGradient = ctx.createRadialGradient(width/2, height, 0, width/2, height, height);
        bgGradient.addColorStop(0, "rgba(212, 140, 17, 0.05)"); 
        bgGradient.addColorStop(1, "transparent");
        ctx.fillStyle = bgGradient;
        ctx.fillRect(0, 0, width, height);

        updateStars();
        drawStars();

        updateShootingStar();
        drawShootingStar();

        requestAnimationFrame(render);
    }

    init();
});
