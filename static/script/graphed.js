import {api} from '/static/script/api.js';

var canvas;
var ctx;
var overlay;
var nodes = [];

function createDiv() {
  var div = document.createElement('div');
  div.classList.add('note');
  overlay.appendChild(div);
  return div;
}

function Node() {
  this.x = canvas.width / 2;
  this.y = canvas.height / 2;
  this.Fx = 0;
  this.Fy = 0;
  this.neighbours = [];
  this.div = createDiv();
  this.div.style.top = this.x + "px";
  this.div.style.left = this.y + "px";

  this.renderEdges = function(ctx) {
    ctx.strokeStyle = "black";
    ctx.lineWidth = 3;
    for (var neighbour of this.neighbours) {
      ctx.beginPath();
      ctx.moveTo(this.x, this.y);
      ctx.lineTo(neighbour.x, neighbour.y);
      ctx.stroke();
    }
  };

  this.update = function() {
    this.x += this.Fx;
    this.y += this.Fy;
    this.div.style.top = this.x + "px";
    this.div.style.left = this.y + "px";
  };

  this.addNeighbour = function(node) {
    if (!this.neighbours.includes(node))
      this.neighbours.push(node);
  };

  this.setPosition = function(x, y) {
    this.x = x;
    this.y = y;
  };
}

function distance(x1, x2, y1, y2) {
  return (x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1);
}

function nDistance(node1, node2) {
  return distance(node1.x, node2.x, node1.y, node2.y);
}

function update() {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;

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
          fspringx += 0.0025 * Math.log(temp) * (other.x - node.x);
          fspringy += 0.0025 * Math.log(temp) * (other.y - node.y);
        }
        frepx += 100 / (nDistance(other, node)) * (node.x - other.x);
        frepy += 100 / (nDistance(other, node)) * (node.y - other.y);
      }
    }

    node.Fx = frepx + fspringx;
    node.Fy = frepy + fspringy;
  }

  for (var node of nodes)
    node.update();

  render();
  window.requestAnimationFrame(update);
}

function render() {
  ctx.fillStyle = "#BBB";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  for (var node of nodes)
    node.renderEdges(ctx);
}

function addNode(node) { nodes.push(node); }

function getMousePos(canvas, evt) {
  var rect = canvas.getBoundingClientRect();
  return {x : evt.clientX - rect.left, y : evt.clientY - rect.top};
}

$(document).ready(function() {
  overlay = document.getElementById('overlay');
  canvas = document.getElementById('graph');
  ctx = canvas.getContext('2d');
  update();

  canvas.addEventListener('mousemove', function(evt) {
    var mousePos = getMousePos(canvas, evt);
    for (var node in nodes) {
      /* if (nodes[node].bounds(mousePos.x, mousePos.y))
        nodes[node].hover = true;
      else
        nodes[node].hover = false;

      if (nodes[node].selected) {
        nodes[node].x = mousePos.x;
        nodes[node].y = mousePos.y;
      }*/
    }
  }, false);

  canvas.addEventListener('mousedown', function(evt) {
    var mousePos = getMousePos(canvas, evt);
    for (var node in nodes) {
      /*if (nodes[node].bounds(mousePos.x, mousePos.y)) {
        nodes[node].selected = true;
        break;
      }*/
    }
  }, false);

  canvas.addEventListener('mouseup', function(evt) {
    // for (var node in nodes)
    //   nodes[node].selected = false;
  }, false);

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
});
