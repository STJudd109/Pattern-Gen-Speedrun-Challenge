// Core variables
let scene, camera, renderer, world;
let objects = [];
let effectors = [];
let isPlacementMode = false;
let raycaster = new THREE.Raycaster();
let mouse = new THREE.Vector2();
let clock = new THREE.Clock();

// Physics world setup
const timeStep = 1 / 60;
const gravity = -9.82;

// Mode variables
let currentMode = 'view';
let physicsEnabled = true;
let placementPreview = null;

// Bounds checking constants
const BOUNDS = {
    minX: -50,
    maxX: 50,
    minZ: -50,
    maxZ: 50,
    minY: -50  // Objects below this Y value will be removed
};

// First, make sure STRUCTURES is properly defined at the top level of your file
const STRUCTURES = {
    wall: {
        name: 'Wall',
        build: (position, scale, blockSize) => {
            console.log('Building wall with:', { position, scale, blockSize });
            const blocks = [];
            const rows = 6;
            const cols = 10;
            const baseY = position.y;

            for (let row = 0; row < rows; row++) {
                for (let col = 0; col < cols; col++) {
                    blocks.push({
                        position: new THREE.Vector3(
                            position.x + (col - cols/2) * (blockSize * 2.1) * scale,
                            baseY + (row + 0.5) * (blockSize * 2.1) * scale, // Added 0.5 to raise blocks
                            position.z
                        ),
                        dimensions: {
                            width: blockSize * scale,
                            height: blockSize * scale,
                            depth: blockSize * scale
                        },
                        type: 'cube'
                    });
                }
            }
            console.log('Generated blocks:', blocks);
            return blocks;
        }
    },
    // ... other structures remain the same
};

// Initialize the scene
function init() {
    // Scene setup
    scene = new THREE.Scene();
    scene.background = new THREE.Color(0x1a1a1a);
    
    // Camera setup
    camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    camera.position.set(0, 15, 30);
    camera.lookAt(0, 0, 0);

    // Renderer setup
    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(window.innerWidth, window.innerHeight);
    renderer.shadowMap.enabled = true;
    document.body.appendChild(renderer.domElement);

    // Physics world setup
    world = new CANNON.World();
    world.gravity.set(0, -9.82, 0);
    world.broadphase = new CANNON.NaiveBroadphase();
    world.solver.iterations = 10;
    world.defaultContactMaterial.friction = 0.5;
    world.defaultContactMaterial.restitution = 0.3;

    // Add ground
    addGround();
    
    // Add lights
    addLights();

    // Add event listeners
    window.addEventListener('resize', onWindowResize, false);
    window.addEventListener('mousemove', onMouseMove, false);
    window.addEventListener('click', onClick, false);

    // Add stats display
    addStatsDisplay();

    // Start animation
    animate();
}

// Add ground plane
function addGround() {
    // Create ground plane
    const groundGeometry = new THREE.PlaneGeometry(
        BOUNDS.maxX - BOUNDS.minX,
        BOUNDS.maxZ - BOUNDS.minZ
    );
    const groundMaterial = new THREE.MeshStandardMaterial({ 
        color: 0x333333,
        roughness: 0.8,
        metalness: 0.2
    });
    const groundMesh = new THREE.Mesh(groundGeometry, groundMaterial);
    groundMesh.rotation.x = -Math.PI / 2;
    groundMesh.receiveShadow = true;
    scene.add(groundMesh);

    // Add grid helper to visualize bounds
    const gridHelper = new THREE.GridHelper(
        BOUNDS.maxX * 2,
        20,
        0x444444,
        0x222222
    );
    scene.add(gridHelper);

    // Add bounds visualization
    const boundsGeometry = new THREE.BoxGeometry(
        BOUNDS.maxX * 2,
        0.1,
        BOUNDS.maxZ * 2
    );
    const boundsMaterial = new THREE.MeshBasicMaterial({ 
        color: 0x00ff00,
        wireframe: true,
        transparent: true,
        opacity: 0.2
    });
    const boundsMesh = new THREE.Mesh(boundsGeometry, boundsMaterial);
    boundsMesh.position.y = 0.05;
    scene.add(boundsMesh);

    // Cannon.js ground
    const groundShape = new CANNON.Plane();
    const groundBody = new CANNON.Body({ mass: 0 });
    groundBody.addShape(groundShape);
    groundBody.quaternion.setFromAxisAngle(new CANNON.Vec3(1, 0, 0), -Math.PI / 2);
    world.addBody(groundBody);
}

// Add lights to the scene
function addLights() {
    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 1);
    directionalLight.position.set(10, 20, 10);
    directionalLight.castShadow = true;
    directionalLight.shadow.camera.near = 0.1;
    directionalLight.shadow.camera.far = 100;
    directionalLight.shadow.camera.left = -20;
    directionalLight.shadow.camera.right = 20;
    directionalLight.shadow.camera.top = 20;
    directionalLight.shadow.camera.bottom = -20;
    scene.add(directionalLight);
}

// Create physics object
function createPhysicsObject(position) {
    const type = document.getElementById('objectType').value;
    const size = parseFloat(document.getElementById('objectSize').value);
    const mass = parseFloat(document.getElementById('objectMass').value);

    let mesh, shape, body;

    // Create Three.js mesh
    switch(type) {
        case 'sphere':
            mesh = new THREE.Mesh(
                new THREE.SphereGeometry(size),
                new THREE.MeshStandardMaterial({ color: Math.random() * 0xffffff })
            );
            shape = new CANNON.Sphere(size);
            break;
        case 'cube':
            mesh = new THREE.Mesh(
                new THREE.BoxGeometry(size, size, size),
                new THREE.MeshStandardMaterial({ color: Math.random() * 0xffffff })
            );
            shape = new CANNON.Box(new CANNON.Vec3(size/2, size/2, size/2));
            break;
        case 'cylinder':
            mesh = new THREE.Mesh(
                new THREE.CylinderGeometry(size/2, size/2, size, 32),
                new THREE.MeshStandardMaterial({ color: Math.random() * 0xffffff })
            );
            shape = new CANNON.Cylinder(size/2, size/2, size, 32);
            break;
    }

    mesh.castShadow = true;
    mesh.receiveShadow = true;
    scene.add(mesh);

    // Create Cannon.js body
    body = new CANNON.Body({ mass: mass });
    body.addShape(shape);
    body.position.copy(position);
    world.addBody(body);

    // Store the object
    objects.push({ mesh, body });
}

// Create effector
function createEffector(position) {
    const type = document.getElementById('effectorType').value;
    const strength = parseFloat(document.getElementById('effectorStrength').value);
    const radius = parseFloat(document.getElementById('effectorRadius').value);

    // Create visual representation
    const geometry = new THREE.SphereGeometry(1);
    const material = new THREE.MeshBasicMaterial({ 
        color: getEffectorColor(type),
        transparent: true,
        opacity: 0.5
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.copy(position);
    mesh.scale.set(radius, radius, radius);
    scene.add(mesh);

    // Store effector data
    effectors.push({
        type,
        position,
        strength,
        radius,
        mesh
    });
}

// Get color based on effector type
function getEffectorColor(type) {
    switch(type) {
        case 'gravity': return 0x0000ff;
        case 'repulsor': return 0xff0000;
        case 'vortex': return 0x00ff00;
        default: return 0xffffff;
    }
}

// Apply effector forces
function applyEffectorForces() {
    objects.forEach(obj => {
        effectors.forEach(effector => {
            const distance = new THREE.Vector3()
                .copy(obj.body.position)
                .sub(effector.position);
            
            const length = distance.length();
            if (length < effector.radius) {
                const force = new CANNON.Vec3();
                const strength = effector.strength * (1 - length / effector.radius);

                switch(effector.type) {
                    case 'gravity':
                        force.copy(distance.normalize().multiplyScalar(-strength));
                        break;
                    case 'repulsor':
                        force.copy(distance.normalize().multiplyScalar(strength));
                        break;
                    case 'vortex':
                        const vortexDir = new THREE.Vector3(
                            -distance.z,
                            0,
                            distance.x
                        ).normalize();
                        force.copy(vortexDir.multiplyScalar(strength));
                        break;
                }
                
                obj.body.applyForce(force, obj.body.position);
            }
        });
    });
}

// Animation loop
function animate() {
    requestAnimationFrame(animate);
    
    if (physicsEnabled) {
        const delta = clock.getDelta();
        world.step(timeStep);

        // Update physics objects and check bounds
        objects = objects.filter(obj => {
            obj.mesh.position.copy(obj.body.position);
            obj.mesh.quaternion.copy(obj.body.quaternion);

            // Check if object is out of bounds
            if (isOutOfBounds(obj.body.position)) {
                removeObject(obj);
                return false;
            }
            return true;
        });

        // Apply effector forces
        applyEffectorForces();
    }

    updateStats();
    renderer.render(scene, camera);
}

// Event handlers
function onWindowResize() {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
}

function onMouseMove(event) {
    mouse.x = (event.clientX / window.innerWidth) * 2 - 1;
    mouse.y = -(event.clientY / window.innerHeight) * 2 + 1;

    if (currentMode !== 'view') {
        raycaster.setFromCamera(mouse, camera);
        const intersects = raycaster.intersectObjects(scene.children);
        
        if (intersects.length > 0) {
            const position = intersects[0].point;
            updatePlacementPreview(position);
        }
    }
}

function onClick(event) {
    if (currentMode === 'view') return;

    raycaster.setFromCamera(mouse, camera);
    const intersects = raycaster.intersectObjects(scene.children);
    
    if (intersects.length > 0) {
        const position = intersects[0].point.clone();
        
        switch(currentMode) {
            case 'object':
                position.y += parseFloat(document.getElementById('objectHeight').value);
                createPhysicsObject(position);
                break;
            case 'effector':
                createEffector(position);
                break;
            case 'structure':
                console.log('Structure placement clicked:', position);
                // Keep the X and Z coordinates but reset Y to 0
                position.y = 0;
                createStructure(position);
                break;
        }
    }
}

function togglePlacementMode() {
    isPlacementMode = !isPlacementMode;
    document.getElementById('modeIndicator').style.display = 
        isPlacementMode ? 'block' : 'none';
}

function clearScene() {
    // Remove physics objects
    objects.forEach(obj => {
        scene.remove(obj.mesh);
        world.remove(obj.body);
    });
    objects = [];

    // Remove effectors
    effectors.forEach(effector => {
        scene.remove(effector.mesh);
    });
    effectors = [];
}

// Mode switching
function setMode(mode) {
    currentMode = mode;
    
    // Update UI
    document.querySelectorAll('.mode-btn').forEach(btn => {
        btn.classList.remove('active');
    });
    document.querySelector(`#${mode}ModeBtn`).classList.add('active');
    
    // Show/hide appropriate controls
    document.getElementById('objectControls').style.display = 
        mode === 'object' ? 'block' : 'none';
    document.getElementById('effectorControls').style.display = 
        mode === 'effector' ? 'block' : 'none';
    
    // Update mode indicator
    document.getElementById('modeIndicator').textContent = 
        `${mode.charAt(0).toUpperCase() + mode.slice(1)} Mode`;
    
    // Clear placement preview if exists
    if (placementPreview) {
        scene.remove(placementPreview);
        placementPreview = null;
    }
}

// Add preview functionality
function updatePlacementPreview(position) {
    if (!placementPreview) {
        switch (currentMode) {
            case 'object':
                const geometry = getObjectGeometry();
                const material = new THREE.MeshBasicMaterial({
                    color: 0x00ff00,
                    transparent: true,
                    opacity: 0.5
                });
                placementPreview = new THREE.Mesh(geometry, material);
                scene.add(placementPreview);
                break;

            case 'effector':
                const radius = parseFloat(document.getElementById('effectorRadius').value);
                const effectorGeometry = new THREE.SphereGeometry(radius);
                const effectorMaterial = new THREE.MeshBasicMaterial({
                    color: getEffectorColor(document.getElementById('effectorType').value),
                    transparent: true,
                    opacity: 0.3
                });
                placementPreview = new THREE.Mesh(effectorGeometry, effectorMaterial);
                scene.add(placementPreview);
                break;

            case 'structure':
                // Create a simple wireframe preview for structures
                const structureType = document.getElementById('structureType').value;
                const scale = parseFloat(document.getElementById('structureScale').value);
                const blockSize = parseFloat(document.getElementById('structureBlockSize').value);
                
                // Create a bounding box preview based on structure type
                let previewGeometry;
                switch (structureType) {
                    case 'wall':
                        previewGeometry = new THREE.BoxGeometry(
                            blockSize * 20 * scale, // width
                            blockSize * 12 * scale, // height
                            blockSize * 2 * scale   // depth
                        );
                        break;
                    case 'pyramid':
                        previewGeometry = new THREE.BoxGeometry(
                            blockSize * 10 * scale,
                            blockSize * 10 * scale,
                            blockSize * 10 * scale
                        );
                        break;
                    case 'castle':
                        previewGeometry = new THREE.BoxGeometry(
                            blockSize * 15 * scale,
                            blockSize * 10 * scale,
                            blockSize * 15 * scale
                        );
                        break;
                    case 'tower':
                        previewGeometry = new THREE.CylinderGeometry(
                            blockSize * 4 * scale,
                            blockSize * 4 * scale,
                            blockSize * 16 * scale,
                            8
                        );
                        break;
                    case 'domino':
                        previewGeometry = new THREE.BoxGeometry(
                            blockSize * 22 * scale,
                            blockSize * 4 * scale,
                            blockSize * 2 * scale
                        );
                        break;
                }
                
                const previewMaterial = new THREE.MeshBasicMaterial({
                    color: 0x00ff00,
                    transparent: true,
                    opacity: 0.2,
                    wireframe: true
                });
                placementPreview = new THREE.Mesh(previewGeometry, previewMaterial);
                scene.add(placementPreview);
                break;
        }
    }

    if (placementPreview) {
        if (currentMode === 'object') {
            position.y += parseFloat(document.getElementById('objectHeight').value);
        } else if (currentMode === 'structure') {
            // Adjust position based on structure type
            const structureType = document.getElementById('structureType').value;
            const blockSize = parseFloat(document.getElementById('structureBlockSize').value);
            const scale = parseFloat(document.getElementById('structureScale').value);
            
            // Center the preview at the click position
            position.y += (placementPreview.geometry.parameters.height || blockSize * 2) * scale / 2;
        }
        placementPreview.position.copy(position);
    }
}

// Add event listeners for structure controls
document.addEventListener('DOMContentLoaded', function() {
    // Update preview when structure settings change
    ['structureType', 'structureScale', 'structureBlockSize'].forEach(id => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener('change', function() {
                if (currentMode === 'structure' && placementPreview) {
                    scene.remove(placementPreview);
                    placementPreview = null;
                    
                    // Force preview update
                    raycaster.setFromCamera(mouse, camera);
                    const intersects = raycaster.intersectObjects(scene.children);
                    if (intersects.length > 0) {
                        updatePlacementPreview(intersects[0].point);
                    }
                }
            });
        }
    });
});

// Add physics toggle functionality
function togglePhysics() {
    physicsEnabled = !physicsEnabled;
    const btn = document.getElementById('physicsToggle');
    btn.textContent = physicsEnabled ? 'Pause Physics' : 'Resume Physics';
}

// Add helper function for object geometry
function getObjectGeometry() {
    const type = document.getElementById('objectType').value;
    const size = parseFloat(document.getElementById('objectSize').value);
    
    switch(type) {
        case 'sphere':
            return new THREE.SphereGeometry(size);
        case 'cube':
            return new THREE.BoxGeometry(size, size, size);
        case 'cylinder':
            return new THREE.CylinderGeometry(size/2, size/2, size, 32);
    }
}

// Add value display updates
document.querySelectorAll('input[type="range"]').forEach(input => {
    input.addEventListener('input', function() {
        const display = this.parentElement.querySelector('.value-display');
        if (display) {
            display.textContent = this.value;
        }
        
        // Update preview if necessary
        if (placementPreview && currentMode === 'effector' && 
            (this.id === 'effectorRadius' || this.id === 'effectorType')) {
            scene.remove(placementPreview);
            placementPreview = null;
        }
    });
});

// Add stats display to show object count
function addStatsDisplay() {
    const stats = document.createElement('div');
    stats.id = 'statsDisplay';
    stats.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        background: rgba(0, 0, 0, 0.7);
        color: white;
        padding: 10px;
        border-radius: 5px;
        font-family: monospace;
    `;
    document.body.appendChild(stats);
}

// Update stats in animation loop
function updateStats() {
    const stats = document.getElementById('statsDisplay');
    if (stats) {
        stats.textContent = `Objects: ${objects.length}`;
    }
}

// Check if an object is out of bounds
function isOutOfBounds(position) {
    return position.x < BOUNDS.minX || position.x > BOUNDS.maxX ||
           position.z < BOUNDS.minZ || position.z > BOUNDS.maxZ ||
           position.y < BOUNDS.minY;
}

// Remove an object
function removeObject(object) {
    // Remove from scene
    scene.remove(object.mesh);
    // Remove from physics world
    world.remove(object.body);
    // Remove from objects array
    const index = objects.indexOf(object);
    if (index > -1) {
        objects.splice(index, 1);
    }
}

// Update createStructure function with better error handling and logging
function createStructure(position) {
    console.log('Creating structure at position:', position);
    const structureType = document.getElementById('structureType').value;
    const scale = parseFloat(document.getElementById('structureScale').value);
    const blockSize = parseFloat(document.getElementById('structureBlockSize').value);
    
    console.log('Structure settings:', {
        type: structureType,
        scale: scale,
        blockSize: blockSize
    });

    const structure = STRUCTURES[structureType];
    if (!structure) {
        console.error('Invalid structure type:', structureType);
        return;
    }
    
    try {
        const blocks = structure.build(position, scale, blockSize);
        console.log(`Creating ${blocks.length} blocks for structure`);
        
        blocks.forEach((block, index) => {
            try {
                // Create Three.js mesh
                let geometry;
                if (block.type === 'cube') {
                    geometry = new THREE.BoxGeometry(
                        block.dimensions.width,
                        block.dimensions.height,
                        block.dimensions.depth
                    );
                } else if (block.type === 'cylinder') {
                    geometry = new THREE.CylinderGeometry(
                        block.size/2,
                        block.size/2,
                        block.size,
                        8
                    );
                }

                const material = new THREE.MeshStandardMaterial({ 
                    color: Math.random() * 0xffffff,
                    roughness: 0.7,
                    metalness: 0.3
                });

                const mesh = new THREE.Mesh(geometry, material);
                mesh.castShadow = true;
                mesh.receiveShadow = true;
                mesh.position.copy(block.position);
                scene.add(mesh);

                // Create Cannon.js body
                let shape;
                if (block.type === 'cube') {
                    shape = new CANNON.Box(new CANNON.Vec3(
                        block.dimensions.width / 2,
                        block.dimensions.height / 2,
                        block.dimensions.depth / 2
                    ));
                } else if (block.type === 'cylinder') {
                    shape = new CANNON.Cylinder(
                        block.size/2,
                        block.size/2,
                        block.size,
                        8
                    );
                }

                const body = new CANNON.Body({
                    mass: 1,
                    material: new CANNON.Material({
                        friction: 0.5,
                        restitution: 0.3
                    })
                });

                body.addShape(shape);
                body.position.copy(block.position);
                world.addBody(body);

                // Store the object
                objects.push({ mesh, body });
                console.log(`Block ${index} created successfully`);
            } catch (error) {
                console.error(`Error creating block ${index}:`, error);
            }
        });
    } catch (error) {
        console.error('Error in createStructure:', error);
    }
}

// Add this helper function to convert Three.js vectors to CANNON.js vectors
function threeToCannonVector(threeVector) {
    return new CANNON.Vec3(threeVector.x, threeVector.y, threeVector.z);
}

// Initialize the scene when the page loads
window.addEventListener('load', init); 