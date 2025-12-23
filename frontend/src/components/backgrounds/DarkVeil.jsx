import { useRef, useEffect } from "react";
import { Renderer, Program, Mesh, Triangle, Vec2 } from "ogl";
import "./DarkVeil.css";

const vertex = `
attribute vec2 position;
void main(){
  gl_Position = vec4(position, 0.0, 1.0);
}
`;

const fragment = `
precision highp float;

uniform vec2 uResolution;
uniform float uTime;

float wave(vec2 uv, float speed, float freq, float shift) {
  return sin(uv.x * freq + uTime * speed + shift) * 0.5 + 0.5;
}

/* Ruido suave tipo aurora */
float fbm(vec2 p){
    float v = 0.0;
    float a = 0.5;
    vec2 shift = vec2(1.0, 2.0);
    for(int i = 0; i < 4; i++){
        v += a * sin(p.x + sin(p.y));
        p = p * 2.0 + shift;
        a *= 0.5;
    }
    return v;
}

void main() {
  vec2 uv = gl_FragCoord.xy / uResolution.xy;
  uv = uv * 2.0 - 1.0;

  // ---- POSICIONAMIENTO SUAVE ----
  uv.x *= 0.12 * (uResolution.x / uResolution.y);
  uv.y *= 1.9;
  uv.y -= 0.64; //arriba

  // --- BASE DE ONDAS ---
  float base = wave(uv, 1.8, 2.5, 0.0)
             + wave(uv, 1.1, 3.5, 1.4)
             + wave(uv, 0.6, 2.0, 2.6);

  base /= 3.0;

  // ---- HALO ORGÁNICO MUY SUAVE ----
  float halo = fbm(uv * 2.5 + uTime * 0.15);

  float dist = length(uv);
  float edgeGlow = smoothstep(0.5, 0.15, dist) * halo;

  // ==== NUEVA PALETA DE COLORES (AZUL / TEAL) ====
  vec3 deepNavy   = vec3(0.02, 0.06, 0.12);  // azul petróleo
  vec3 deepBlue   = vec3(0.05, 0.18, 0.35);  // azul profundo
  vec3 tealAccent = vec3(0.10, 0.55, 0.55);  // teal frío
  vec3 cyanSoft   = vec3(0.45, 0.80, 0.85);  // cyan suave

  // Mezcla base
  vec3 color = mix(deepNavy, deepBlue, base);

  // Halo teal/cyan MUY sutil
  color += tealAccent * edgeGlow * 0.4;
  color += cyanSoft * edgeGlow * 0.15;

  // Viñeta natural
  float vignette = smoothstep(1.3, 0.3, dist);
  color *= vignette;

  gl_FragColor = vec4(color, 1.0);
}
`;

export default function DarkVeil() {
  const canvasRef = useRef();

  useEffect(() => {
    const canvas = canvasRef.current;

    const renderer = new Renderer({
      dpr: Math.min(window.devicePixelRatio, 2),
      canvas,
      antialias: false,
    });

    const gl = renderer.gl;

    const geometry = new Triangle(gl, {
      position: {
        size: 2,
        data: new Float32Array([
          -1, -1,
          3, -1,
          -1, 3,
        ]),
      },
    });

    const program = new Program(gl, {
      vertex,
      fragment,
      uniforms: {
        uTime: { value: 0 },
        uResolution: { value: new Vec2() },
      },
    });

    const mesh = new Mesh(gl, { geometry, program });

    const resize = () => {
      const w = window.innerWidth;
      const h = window.innerHeight;
      renderer.setSize(w, h);
      program.uniforms.uResolution.value.set(w, h);
    };

    window.addEventListener("resize", resize);
    resize();

    const start = performance.now();
    let frame;

    const loop = () => {
      program.uniforms.uTime.value = (performance.now() - start) / 1000;
      renderer.render({ scene: mesh });
      frame = requestAnimationFrame(loop);
    };

    loop();

    return () => {
      cancelAnimationFrame(frame);
      window.removeEventListener("resize", resize);
    };
  }, []);

  return <canvas ref={canvasRef} className="darkveil-canvas" />;
}
