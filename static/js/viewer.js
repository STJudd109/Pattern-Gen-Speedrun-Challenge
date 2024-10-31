let scene, camera, renderer;

function init() {
    // Create scene
    scene = new THREE.Scene();
    
    // Create camera
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.z = 30;
    
    // Create renderer
    renderer = new THREE.WebGLRenderer();
    renderer.setSize(window.innerWidth, window.innerHeight);
    document.body.appendChild(renderer.domElement);
    
    // Add button event listeners
    document.getElementById('refreshBtn').addEventListener('click', () => {
        clearPattern();
        fetchPattern();
    });
    
    document.getElementById('shuffleBtn').addEventListener('click', () => {
        clearPattern();
        fetchPattern('?shuffle=true');
    });
    
    // Fetch and display pattern
    fetchPattern();
    
    // Add lights
    const light = new THREE.DirectionalLight(0xffffff, 1);
    light.position.set(1, 1, 1);
    scene.add(light);
    
    // Start animation
    animate();
}

function clearPattern() {
    // Remove existing pattern
    scene.children = scene.children.filter(child => !(child instanceof THREE.Points));
}

async function fetchPattern(params = '') {
    const response = await fetch('/generate' + params);
    const data = await response.json();
    
    const geometry = new THREE.BufferGeometry();
    geometry.setAttribute('position', new THREE.Float32BufferAttribute(data.vertices, 3));
    
    const material = new THREE.PointsMaterial({
        color: 0x00ff00,
        size: 0.1
    });
    
    const points = new THREE.Points(geometry, material);
    scene.add(points);
}

function animate() {
    requestAnimationFrame(animate);
    renderer.render(scene, camera);
}

// Start the visualization
init();