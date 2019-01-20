import {api} from '/static/script/api.js';

var canvas;
var ctx;
var overlay;
var nodes = [];
var z = 1;
var offset = [ 0, 0 ];

function createDiv() { return div; }

function Node() {
  this.x = canvas.width / 2;
  this.y = canvas.height / 2;
  this.Fx = 0;
  this.Fy = 0;
  this.neighbours = [];

  this.div = document.createElement('div');
  var shrink = document.createElement('div');
  shrink.classList.add('shrink');
  shrink.appendChild(document.createTextNode('x'));
  shrink.addEventListener('click', () => { this.shrink(); });
  this.div.appendChild(shrink);
  this.div.classList.add('note');
  overlay.appendChild(this.div);

  this.div.style.top = this.x + "px";
  this.div.style.left = this.y + "px";
  this.expanded = false;
  this.selected = false;

  this.expand = function() {
    if (!this.expanded) {
      this.expanded = true;
      this.div.classList.add('expanded');
    }
    this.div.style["z-index"] = z;
    z += 1;
  };

  this.shrink = function() {
    if (this.expanded) {
      this.div.classList.remove('expanded');
      this.expanded = false;
    }
    this.div.style["z-index"] = 0;
  };

  this.renderEdges = function(ctx) {
    ctx.strokeStyle = "#CCC";
    ctx.lineWidth = 3;
    var rect = this.div.getBoundingClientRect();
    for (var neighbour of this.neighbours) {
      var other = neighbour.div.getBoundingClientRect();
      ctx.beginPath();
      ctx.moveTo(this.x, this.y);
      ctx.lineTo(neighbour.x, neighbour.y);
      ctx.stroke();
    }
  };

  this.update = function() {
    if (!this.expanded)
      this.setPosition(this.x + this.Fx, this.y + this.Fy);
    else
      this.setPosition(this.x, this.y);
  };

  this.addNeighbour = function(node) {
    if (!this.neighbours.includes(node))
      this.neighbours.push(node);
  };

  this.setPosition = function(x, y) {
    this.x = x;
    this.y = y;
    this.div.style.left = (this.x - this.div.offsetWidth / 2) + "px";
    this.div.style.top = (this.y - this.div.offsetHeight / 2) + "px";
  };

  this.contains = function(x, y) {
    var rect = this.div.getBoundingClientRect();
    return x > rect.left && x < rect.left + rect.width && y > rect.top &&
           y < rect.top + rect.height;
  };

  this.intersects = function(node) {
    var rect = this.div.getBoundingClientRect();
    var other = node.div.getBoundingClientRect();
    return !(rect.left + rect.width + 50 < other.left ||
             other.left + other.width + 50 < rect.left ||
             rect.top + rect.height + 50 < other.top ||
             other.top + other.height + 50 < rect.top);
  };
}

function distance(x1, x2, y1, y2) {
  return (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1);
}

function nDistance(node1, node2) {
  return distance(node1.x, node2.x, node1.y, node2.y);
}

function update() {
  var overlayRect = overlay.getBoundingClientRect();
  canvas.width = overlayRect.width;
  canvas.height = overlayRect.height;

  for (var node of nodes) {
    var frepx = 0;
    var frepy = 0;
    var fspringx = 0;
    var fspringy = 0;

    for (var other of nodes) {
      if (node !== other) {
        if (node.neighbours.includes(other) ||
            other.neighbours.includes(node)) {
          var temp = nDistance(other, node);
          if (!other.expanded) {
            fspringx += 0.0025 * Math.log(temp) * (other.x - node.x);
            fspringy += 0.0025 * Math.log(temp) * (other.y - node.y);
          } else {
            fspringx += 0.00075 * Math.log(temp) * (other.x - node.x);
            fspringy += 0.00075 * Math.log(temp) * (other.y - node.y);
          }
        }
        frepx += 500 / (nDistance(other, node)) * (node.x - other.x);
        frepy += 500 / (nDistance(other, node)) * (node.y - other.y);
      }
    }

    node.Fx = frepx + fspringx;
    node.Fy = frepy + fspringy;
  }

  for (var node of nodes) {
    if (!node.selected)
      node.update();
  }

  render();
  window.requestAnimationFrame(update);
}

function render() {
  ctx.fillStyle = "#FCFCFC";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  for (var node of nodes)
    node.renderEdges(ctx);
}

function addNode(node) { nodes.push(node); }

function getMousePos(target, e) {
  var rect = target.getBoundingClientRect();
  return {x : e.clientX - rect.left, y : e.clientY - rect.top};
}

$(document).ready(function() {
  overlay = document.getElementById('overlay');
  canvas = document.getElementById('graph');
  ctx = canvas.getContext('2d');
  update();

  overlay.addEventListener('mousemove', function(e) {
    var mousePos = getMousePos(overlay, e);
    for (var node of nodes) {
      if (node.selected) {
        node.setPosition(mousePos.x - offset[0], mousePos.y - offset[1]);
        break;
      }
    }
  }, false);

  overlay.addEventListener('mousedown', function(e) {
    var mousePos = getMousePos(overlay, e);
    for (var node of nodes) {
      node.selected = false;
    }
    for (var node of nodes) {
      if (node.contains(mousePos.x, mousePos.y)) {
        var rect = node.div.getBoundingClientRect();
        offset = [
          mousePos.x - (rect.left + rect.width / 2),
          mousePos.y - (rect.top + rect.height / 2)
        ];
        node.selected = true;
        node.expand();
        break;
      }
    }
  });

  overlay.addEventListener('mouseup', function(e) {
    for (var node of nodes) {
      node.selected = false;
    }
  });

  var node1 = new Node();
  addNode(node1);
  var node2 = new Node();
  node2.setPosition(300, 400);
  addNode(node2);
  node1.addNeighbour(node2);
  var node3 = new Node();
  addNode(node3);
  node3.setPosition(800, 600);
  node1.addNeighbour(node3);
  node2.addNeighbour(node3);
  var node4 = new Node();
  addNode(node4);
  node4.setPosition(800, 601);
  node3.addNeighbour(node4);
  var node5 = new Node();
  addNode(node5);
  node5.setPosition(800, 605);
  node5.addNeighbour(node3);
});
