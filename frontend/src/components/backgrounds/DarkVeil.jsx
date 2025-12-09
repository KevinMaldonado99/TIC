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
    for(int i = 0; i < 5; i++){
        v += a * sin(p.x + sin(p.y));
        p = p * 2.0 + shift;
        a *= 0.5;
    }
    return v;
}

void main() {
  vec2 uv = gl_FragCoord.xy / uResolution.xy;
  uv = uv * 2.0 - 1.0;

  // ---- CENTRAR & POSICIONAR ----
  uv.x = uv.x * 0.1 * (uResolution.x / uResolution.y); //para ensanchar o reducer el ancho bajar = 0.1
  //
  uv.y *= 0.8;

  uv.x -= 0.1;   // mover derecha 
  uv.y -= 0.08;   // mover arriba

  // --- NEBULOSA PRINCIPAL ---
  float base = wave(uv, 2.0, 3.0, 0.0)
             + wave(uv, 3.0, 4.0, 1.3)
             + wave(uv, 1.7, 2.5, 2.8);

  base /= 3.0;

  // ---- ONDAS ORGÁNICAS ESTILO AURORA ----
  float halo = fbm(uv * 3.0 + uTime * 0.2);

  // Bordes suaves, NO círculo perfecto:
  float dist = length(uv);
  float edgeGlow = smoothstep(0.4, 0.1, dist) * halo;

  // ==== PALETA DE COLORES ====
  vec3 coreBlue = vec3(0.0, 0.0, 1.0);
  vec3 deepBlue = vec3(0.0, 0.0, 0.3);

  // Halo rosado eléctrico como Vanta Halo
  vec3 electricPink = vec3(1.0, 0.1, 0.7);

  // Mezclar colores
  vec3 color = mix(deepBlue, coreBlue, base);

  // Añadir halo rosado dinámico
  color += electricPink * edgeGlow * 0.8;

  // Viñeta natural
  float vignette = smoothstep(1.2, 0.2, dist);
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
          1, -1,    
          -1, 1     // SOLO HASTA ARRIBA, NO VA MÁS ABAJO
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
