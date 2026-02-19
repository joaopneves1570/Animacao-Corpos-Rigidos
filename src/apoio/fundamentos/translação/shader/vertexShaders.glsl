#version 460 core

uniform mat4 ModelMatrix;

layout(location = 0) in vec2 a_pos;
layout(location = 1) in vec3 a_color;

out vec3 color;

void main(){
    color = a_color;
    gl_Position = ModelMatrix * vec4(a_pos, 0.0, 1.0);
}
