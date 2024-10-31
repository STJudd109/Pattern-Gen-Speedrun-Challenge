document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.getElementById('visualizer');
    const ctx = canvas.getContext('2d');
    let points = [];

    const settings = {
        pulseSpeed: 0.05,
        pulseAmount: 0.2,
        baseRadius: 5,
        numPoints: 50,
        connectionDistance: 100,
        pointColor: '#000000',
        connectionColor: '#000000',
        maxConnections: 3,
        newPointRadius: 5,
        dragForce: 0.9,
        fluidFriction: 0.95,
        fluidRange: 200,
        repulsionForce: 0.5
    };

    class Point {
        constructor(x, y, radius) {
            this.x = x;
            this.y = y;
            this.baseRadius = radius;
            this.radius = radius;
            this.phase = Math.random() * Math.PI * 2;
            this.pulseSpeed = settings.pulseSpeed;
            this.pulseAmount = settings.pulseAmount;
            this.connections = []; // Array to store connected points
            this.vx = 0;
            this.vy = 0;
            this.isDragging = false;
            this.isManual = false;
        }

        update() {
            this.phase += this.pulseSpeed;
            const pulseFactor = 1 + Math.sin(this.phase) * this.pulseAmount;
            this.radius = this.baseRadius * pulseFactor;

            if (!this.isDragging) {
                this.x += this.vx;
                this.y += this.vy;
                
                this.vx *= settings.fluidFriction;
                this.vy *= settings.fluidFriction;

                if (this.x < 0 || this.x > canvas.width) {
                    this.vx *= -0.5;
                    this.x = Math.max(0, Math.min(this.x, canvas.width));
                }
                if (this.y < 0 || this.y > canvas.height) {
                    this.vy *= -0.5;
                    this.y = Math.max(0, Math.min(this.y, canvas.height));
                }
            }
        }

        draw(ctx) {
            ctx.fillStyle = settings.pointColor;
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    function findNearestNeighbors(point, maxConnections) {
        return points
            .filter(p => p !== point)
            .map(p => ({
                point: p,
                distance: Math.sqrt(
                    Math.pow(p.x - point.x, 2) + 
                    Math.pow(p.y - point.y, 2)
                )
            }))
            .sort((a, b) => a.distance - b.distance)
            .slice(0, maxConnections)
            .map(p => p.point);
    }

    function drawConnections(ctx) {
        // Draw regular connections
        ctx.strokeStyle = settings.connectionColor;
        ctx.lineWidth = 1;
        
        for (let i = 0; i < points.length; i++) {
            for (let j = i + 1; j < points.length; j++) {
                const dx = points[i].x - points[j].x;
                const dy = points[i].y - points[j].y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < settings.connectionDistance) {
                    const opacity = 1 - (distance / settings.connectionDistance);
                    ctx.globalAlpha = opacity;
                    ctx.beginPath();
                    ctx.moveTo(points[i].x, points[i].y);
                    ctx.lineTo(points[j].x, points[j].y);
                    ctx.stroke();
                }
            }
        }

        // Draw clicked connections
        ctx.globalAlpha = 1;
        ctx.strokeStyle = '#FF0000';
        ctx.lineWidth = 2;

        points.forEach(point => {
            if (point.connections.length > 0) {
                point.connections.forEach(neighbor => {
                    ctx.beginPath();
                    ctx.moveTo(point.x, point.y);
                    ctx.lineTo(neighbor.x, neighbor.y);
                    ctx.stroke();
                });
            }
        });

        // Reset styles
        ctx.globalAlpha = 1;
        ctx.strokeStyle = settings.connectionColor;
        ctx.lineWidth = 1;
    }

    function updatePoints() {
        points = [];
        for (let i = 0; i < settings.numPoints; i++) {
            const x = Math.random() * canvas.width;
            const y = Math.random() * canvas.height;
            points.push(new Point(x, y, settings.baseRadius));
        }
    }

    function handleResize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
        updatePoints();
    }

    function animate() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        drawConnections(ctx);
        points.forEach(point => {
            point.update();
            point.draw(ctx);
        });
        requestAnimationFrame(animate);
    }

    // Add click handler
    canvas.addEventListener('click', (event) => {
        const rect = canvas.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;
        
        const newPoint = new Point(x, y, settings.newPointRadius);
        newPoint.connections = findNearestNeighbors(newPoint, settings.maxConnections);
        points.push(newPoint);
        
        // Update UI counter
        const numPointsInput = document.getElementById('numPoints');
        if (numPointsInput) {
            numPointsInput.value = points.length;
            document.getElementById('numPointsValue').textContent = points.length;
        }
    });

    // Event Listeners
    document.getElementById('pulseSpeed').addEventListener('input', (e) => {
        settings.pulseSpeed = parseFloat(e.target.value);
        document.getElementById('pulseSpeedValue').textContent = e.target.value;
        points.forEach(point => point.pulseSpeed = settings.pulseSpeed);
    });

    document.getElementById('pulseAmount').addEventListener('input', (e) => {
        settings.pulseAmount = parseFloat(e.target.value);
        document.getElementById('pulseAmountValue').textContent = e.target.value;
        points.forEach(point => point.pulseAmount = settings.pulseAmount);
    });

    document.getElementById('baseRadius').addEventListener('input', (e) => {
        settings.baseRadius = parseFloat(e.target.value);
        document.getElementById('baseRadiusValue').textContent = e.target.value;
        points.forEach(point => point.baseRadius = settings.baseRadius);
    });

    document.getElementById('numPoints').addEventListener('input', (e) => {
        settings.numPoints = parseInt(e.target.value);
        document.getElementById('numPointsValue').textContent = e.target.value;
        updatePoints();
    });

    document.getElementById('connectionDistance').addEventListener('input', (e) => {
        settings.connectionDistance = parseFloat(e.target.value);
        document.getElementById('connectionDistanceValue').textContent = e.target.value;
    });

    document.getElementById('pointColor').addEventListener('input', (e) => {
        settings.pointColor = e.target.value;
    });

    document.getElementById('connectionColor').addEventListener('input', (e) => {
        settings.connectionColor = e.target.value;
    });

    document.getElementById('maxConnections').addEventListener('input', (e) => {
        settings.maxConnections = parseInt(e.target.value);
        document.getElementById('maxConnectionsValue').textContent = e.target.value;
    });

    window.addEventListener('resize', handleResize);

    // Initialize
    handleResize();
    updatePoints();
    animate();

    let isDragging = false;
    let draggedPoint = null;
    let lastMouseX = 0;
    let lastMouseY = 0;

    canvas.addEventListener('mousedown', (event) => {
        const rect = canvas.getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;

        const clickedPoint = points.find(point => {
            const dx = point.x - mouseX;
            const dy = point.y - mouseY;
            return Math.sqrt(dx * dx + dy * dy) < point.radius * 2;
        });

        if (clickedPoint) {
            isDragging = true;
            draggedPoint = clickedPoint;
            draggedPoint.isDragging = true;
        } else {
            const newPoint = new Point(mouseX, mouseY, settings.newPointRadius);
            newPoint.isManual = true;
            newPoint.connections = findNearestNeighbors(newPoint, settings.maxConnections);
            points.push(newPoint);
            isDragging = true;
            draggedPoint = newPoint;
            draggedPoint.isDragging = true;
        }

        lastMouseX = mouseX;
        lastMouseY = mouseY;
    });

    canvas.addEventListener('mousemove', (event) => {
        if (!isDragging || !draggedPoint) return;

        const rect = canvas.getBoundingClientRect();
        const mouseX = event.clientX - rect.left;
        const mouseY = event.clientY - rect.top;

        const dx = mouseX - lastMouseX;
        const dy = mouseY - lastMouseY;

        draggedPoint.x = mouseX;
        draggedPoint.y = mouseY;

        points.forEach(point => {
            if (point !== draggedPoint && !point.isDragging) {
                const distX = point.x - draggedPoint.x;
                const distY = point.y - draggedPoint.y;
                const distance = Math.sqrt(distX * distX + distY * distY);

                if (distance < settings.fluidRange) {
                    const force = (1 - distance / settings.fluidRange) * settings.dragForce;
                    point.vx += dx * force;
                    point.vy += dy * force;

                    const repulsion = settings.repulsionForce / (distance + 1);
                    point.vx += (distX / distance) * repulsion;
                    point.vy += (distY / distance) * repulsion;
                }
            }
        });

        lastMouseX = mouseX;
        lastMouseY = mouseY;
    });

    canvas.addEventListener('mouseup', () => {
        if (draggedPoint) {
            draggedPoint.vx = (lastMouseX - draggedPoint.x) * 0.1;
            draggedPoint.vy = (lastMouseY - draggedPoint.y) * 0.1;
            draggedPoint.isDragging = false;
        }
        isDragging = false;
        draggedPoint = null;
    });

    document.getElementById('dragForce').addEventListener('input', (e) => {
        settings.dragForce = parseFloat(e.target.value);
        document.getElementById('dragForceValue').textContent = e.target.value;
    });

    document.getElementById('fluidRange').addEventListener('input', (e) => {
        settings.fluidRange = parseFloat(e.target.value);
        document.getElementById('fluidRangeValue').textContent = e.target.value;
    });

    document.getElementById('repulsionForce').addEventListener('input', (e) => {
        settings.repulsionForce = parseFloat(e.target.value);
        document.getElementById('repulsionForceValue').textContent = e.target.value;
    });
}); 