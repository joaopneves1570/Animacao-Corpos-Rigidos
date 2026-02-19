//Declarando a versão de GLSL
#version 330 core

//Declarações de entrada e saída
layout(location = 0) in vec2 a_pos;
layout(location = 1) in vec3 a_color;

out vec3 f_color;

void main(){
    f_color = a_color;
    gl_Position = vec4(a_pos, 0.0, 1.0);
}