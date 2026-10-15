"use strict";

const $ = id => document.getElementById(id);
const tokenKey = "autogestor_token";
let vehiculos = [];
let usuario = null;
let editandoId = null;
let toastTimer;

const precio = valor => new Intl.NumberFormat("es-MX", {style:"currency",currency:"MXN",maximumFractionDigits:0}).format(Number(valor)||0);
const escapeHTML = valor => String(valor ?? "").replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const principal = v => (v.imagenes || []).find(i=>i.principal) || (v.imagenes||[])[0];
const titulo = v => `${v.marca} ${v.modelo} ${v.año}`;

function toast(mensaje){const el=$("toast");el.textContent=mensaje;el.classList.remove("hidden");clearTimeout(toastTimer);toastTimer=setTimeout(()=>el.classList.add("hidden"),4000);}
function salir(mensaje=""){
 localStorage.removeItem(tokenKey); usuario=null;vehiculos=[];
 $("loginModal").classList.remove("hidden");$("detailModal").classList.add("hidden");
 $("loginError").textContent=mensaje;
}
async function api(ruta, opciones={}){
 const headers={...(opciones.headers||{})};
 const token=localStorage.getItem(tokenKey);
 if(token) headers.Authorization=`Bearer ${token}`;
 if(opciones.body && !(opciones.body instanceof FormData)) headers["Content-Type"]="application/json";
 let respuesta;
 try {respuesta=await fetch(ruta,{...opciones,headers});}catch{throw new Error("No se pudo conectar con el servidor.");}
 if(respuesta.status===401){salir("Tu sesión expiró. Inicia sesión nuevamente.");throw new Error("Sesión expirada");}
 let datos=null;try{datos=await respuesta.json();}catch{}
 if(!respuesta.ok){
  const detalle=datos?.detail;
  throw new Error(typeof detalle==="string"?detalle:Array.isArray(detalle)?detalle.map(e=>e.msg).join("; "):`Error ${respuesta.status}`);
 }
 return datos;
}
function esAdmin(){return usuario?.rol==="admin";}
function aplicarPermisos(){
 document.querySelectorAll(".admin-only,[data-admin='true']").forEach(el=>el.classList.toggle("hidden",!esAdmin()));
 $("sidebarUserName").textContent=usuario?.nombre||usuario?.email||"Usuario";
 $("sidebarUserRole").textContent=esAdmin()?"Administrador":"Usuario";
 $("logoutButton").textContent="Salir";
 $("logoutButton").style.width="auto";$("logoutButton").style.padding="0 12px";
}
function irA(seccion){
 if((seccion==="agregar"||seccion==="usuarios")&&!esAdmin()){toast("No tienes permisos para esta sección.");return;}
 document.querySelectorAll(".page-section").forEach(el=>el.classList.toggle("hidden",el.id!==`section-${seccion}`));
 document.querySelectorAll(".nav-item[data-section]").forEach(el=>el.classList.toggle("active",el.dataset.section===seccion));
 const nombres={dashboard:"Panel de control",vehiculos:"Inventario de vehículos",agregar:"Gestionar vehículo",buscar:"Buscar vehículos",usuarios:"Usuarios"};
 const cabecera=document.querySelector(".topbar h1");if(cabecera)cabecera.textContent=nombres[seccion]||"AutoGestor";
 if(seccion==="vehiculos") renderVehiculos($("inventoryGrid"),vehiculos);
 if(seccion==="buscar") buscar();
 if(seccion==="usuarios") cargarUsuarios();
 window.scrollTo({top:0,behavior:"smooth"});
}
function renderVehiculos(contenedor,lista){
 contenedor.replaceChildren();
 if(!lista.length){contenedor.innerHTML='<div class="notice">No se encontraron vehículos.</div>';return;}
 for(const v of lista){
  const card=document.createElement("article");card.className="vehicle-card";
  const img=principal(v);
  card.innerHTML=`${img?`<img class="vehicle-photo" alt="Foto de ${escapeHTML(titulo(v))}" src="${escapeHTML(img.url)}">`:'<div class="vehicle-photo-empty">Sin fotografía</div>'}
  <div class="vehicle-info"><span class="state-pill ${escapeHTML(v.estado||'disponible')}">${escapeHTML(v.estado||'disponible')}</span><h3>${escapeHTML(titulo(v))}</h3><p>${Number(v.kilometraje||0).toLocaleString('es-MX')} km · ${escapeHTML(v.color||'No especificado')}</p><strong>${precio(v.precio)}</strong><div class="vehicle-actions"><button type="button" data-action="ver">Ver detalles</button>${esAdmin()?'<button type="button" data-action="editar">Editar</button><button type="button" class="danger" data-action="eliminar">Eliminar</button>':''}</div></div>`;
  card.querySelectorAll("[data-action]").forEach(b=>b.addEventListener("click",()=>{
   if(b.dataset.action==="ver") verDetalle(v.id);
   if(b.dataset.action==="editar") abrirFormulario(v.id);
   if(b.dataset.action==="eliminar") eliminarVehiculo(v.id);
  }));contenedor.appendChild(card);
 }
}
function dashboard(){
 const n=vehiculos.length,total=vehiculos.reduce((a,v)=>a+Number(v.precio),0);
 $("totalVehiculos").textContent=n;$("valorInventario").textContent=precio(total);
 $("precioPromedio").textContent=precio(n?total/n:0);
 const conteo={};vehiculos.forEach(v=>conteo[v.marca]=(conteo[v.marca]||0)+1);
 $("totalMarcas").textContent=Object.keys(conteo).length;$("chartTotal").textContent=n;
 $("brandLegend").textContent=Object.entries(conteo).map(([m,c])=>`${m}: ${c}`).join(" · ")||"Sin información";
 const colores=["#1677ff","#39a0ff","#1551a7","#285b83","#172233"];
 let angulo=0;const partes=Object.values(conteo).map((cantidad,i)=>{const inicio=angulo;angulo+=cantidad/n*360;return `${colores[i%colores.length]} ${inicio}deg ${angulo}deg`;});
 document.querySelector(".chart-circle").style.background=n?`conic-gradient(${partes.join(',')})`:"#172233";
 const lista=$("vehiculosLista");lista.replaceChildren();
 if(!n){lista.innerHTML='<div class="loading">No hay vehículos registrados.</div>';return;}
 vehiculos.slice(0,5).forEach(v=>{const fila=document.createElement("div");fila.className="vehicle-row";fila.innerHTML=`<span class="vehicle-brand">${escapeHTML(v.marca)}</span><span class="vehicle-muted">${escapeHTML(v.modelo)}</span><span class="vehicle-muted">${escapeHTML(v.año)}</span><span class="vehicle-price">${precio(v.precio)}</span>`;fila.style.cursor="pointer";fila.addEventListener("click",()=>verDetalle(v.id));lista.appendChild(fila);});
}
async function cargarVehiculos(){
 const acumulados=[];let pagina=1;
 while(pagina<=100){const bloque=await api(`/vehiculos?pagina=${pagina}&limite=100`);if(!Array.isArray(bloque))throw new Error("Respuesta de inventario inesperada");acumulados.push(...bloque);if(bloque.length<100)break;pagina++;}
 vehiculos=acumulados;dashboard();renderVehiculos($("inventoryGrid"),vehiculos);
}
async function iniciar(){
 if(!localStorage.getItem(tokenKey)){salir();return;}
 try{
  // /usuarios/me debe estar registrado en routes/usuarios.py
  usuario=await api("/usuarios/me");
  aplicarPermisos();await cargarVehiculos();$("loginModal").classList.add("hidden");irA("dashboard");
 }catch(e){console.error(e);if(localStorage.getItem(tokenKey)){salir("No se pudo validar tu usuario. Comprueba el endpoint /usuarios/me.");}}
}
function abrirFormulario(id=null){
 if(!esAdmin())return;
 editandoId=id;const v=vehiculos.find(x=>x.id===id);
 $("vehicleForm").reset();$("vehicleImages").value="";
 $("vehicleFormMessage").textContent="";$("vehicleFormMessage").classList.remove("success");
 $("vehicleFormTitle").textContent=v?"Editar vehículo":"Agregar vehículo";
 if(v){for(const [clave,valor] of Object.entries(v)){const input=$("vehicleForm").elements.namedItem(clave);if(input&&clave!=="imagenes")input.value=valor??"";}}
 else {$("vehicleForm").elements.namedItem("kilometraje").value=0;$("vehicleForm").elements.namedItem("color").value="No especificado";}
 mostrarImagenesExistentes(v);irA("agregar");
}
function mostrarImagenesExistentes(v){
 const cont=$("existingImages");cont.replaceChildren();if(!v)return;
 (v.imagenes||[]).forEach(img=>{
  const tile=document.createElement("div");tile.className="photo-tile";
  tile.innerHTML=`<img src="${escapeHTML(img.url)}" alt="Foto del vehículo"><div class="photo-actions"><button data-action="portada" ${img.principal?'disabled':''}>${img.principal?'Portada':'Hacer portada'}</button><button data-action="borrar">Eliminar</button></div>`;
  tile.querySelector('[data-action="portada"]').addEventListener("click",async()=>{try{await api(`/vehiculos/${v.id}/imagenes/${img.id}/principal`,{method:"PUT"});await cargarVehiculos();mostrarImagenesExistentes(vehiculos.find(x=>x.id===v.id));toast("Portada actualizada");}catch(e){toast(e.message);}});
  tile.querySelector('[data-action="borrar"]').addEventListener("click",async()=>{if(!confirm("¿Eliminar esta fotografía?"))return;try{await api(`/vehiculos/${v.id}/imagenes/${img.id}`,{method:"DELETE"});await cargarVehiculos();mostrarImagenesExistentes(vehiculos.find(x=>x.id===v.id));toast("Fotografía eliminada");}catch(e){toast(e.message);}});
  cont.appendChild(tile);
 });
}
async function guardarVehiculo(event){
 event.preventDefault();if(!esAdmin())return;
 const form=$("vehicleForm"), boton=$("saveVehicleButton"), mensaje=$("vehicleFormMessage");
 const datos=Object.fromEntries(new FormData(form).entries());
 datos.año=Number(datos.año);datos.precio=Number(datos.precio);datos.kilometraje=Number(datos.kilometraje);datos.descripcion=datos.descripcion||null;
 const fotos=Array.from($("vehicleImages").files);
 if(fotos.some(f=>f.size>5*1024*1024||!["image/jpeg","image/png","image/webp"].includes(f.type))){mensaje.textContent="Cada fotografía debe ser JPG/PNG/WebP y pesar máximo 5 MB.";return;}
 const existentes=vehiculos.find(v=>v.id===editandoId)?.imagenes?.length||0;
 if(fotos.length+existentes>10){mensaje.textContent="Máximo 10 fotografías por vehículo.";return;}
 boton.disabled=true;mensaje.textContent="Guardando vehículo...";mensaje.classList.remove("success");
 try{
  const idOriginal=editandoId;
  const guardado=await api(idOriginal?`/vehiculos/${idOriginal}`:"/vehiculos",{method:idOriginal?"PUT":"POST",body:JSON.stringify(datos)});
  let fallidas=0;
  for(const foto of fotos){const cuerpo=new FormData();cuerpo.append("archivo",foto);try{await api(`/vehiculos/${guardado.id}/imagenes`,{method:"POST",body:cuerpo});}catch(e){fallidas++;console.error(e);}}
  await cargarVehiculos();
  mensaje.textContent=fallidas?`Vehículo guardado, pero ${fallidas} fotografía(s) no se pudieron subir.`:"Vehículo guardado correctamente.";
  mensaje.classList.add("success");toast(mensaje.textContent);editandoId=null;irA("vehiculos");
 }catch(e){mensaje.textContent=e.message;}finally{boton.disabled=false;}
}
async function eliminarVehiculo(id){
 if(!esAdmin()||!confirm("¿Seguro que deseas eliminar este vehículo y sus fotografías? Esta acción no se puede deshacer."))return;
 try{await api(`/vehiculos/${id}`,{method:"DELETE"});await cargarVehiculos();toast("Vehículo eliminado correctamente");}catch(e){toast(e.message);}
}
async function verDetalle(id){
 try{
  const v=await api(`/vehiculos/${id}`);const fotos=v.imagenes||[];
  $("detailContent").innerHTML=`<p class="small-text">FICHA DEL VEHÍCULO</p><h2>${escapeHTML(titulo(v))}</h2><span class="state-pill ${escapeHTML(v.estado||'disponible')}">${escapeHTML(v.estado||'disponible')}</span><div class="detail-gallery">${fotos.length?fotos.map(i=>`<img src="${escapeHTML(i.url)}" alt="Fotografía de ${escapeHTML(titulo(v))}">`).join(''):'<div class="vehicle-photo-empty">Sin fotografías</div>'}</div><p><strong>${precio(v.precio)}</strong></p><p>Kilometraje: ${Number(v.kilometraje||0).toLocaleString('es-MX')} km</p><p>Color: ${escapeHTML(v.color||'No especificado')}</p><p>${escapeHTML(v.descripcion||'Sin descripción adicional.')}</p>`;
  $("detailModal").classList.remove("hidden");
 }catch(e){toast(e.message);}
}
async function buscar(){
 const datos=new FormData($("searchForm"));const parametros=new URLSearchParams();
 for(const [clave,valor] of datos.entries())if(String(valor).trim())parametros.set(clave,String(valor).trim());
 try{
  // Filtrado completo sobre los registros ya descargados para no perder resultados por paginación.
  const marca=String(datos.get("marca")||"").toLowerCase(),modelo=String(datos.get("modelo")||"").toLowerCase();
  const min=datos.get("precio_min"),max=datos.get("precio_max"),estado=datos.get("estado");
  const lista=vehiculos.filter(v=>v.marca.toLowerCase().includes(marca)&&v.modelo.toLowerCase().includes(modelo)&&(!min||Number(v.precio)>=Number(min))&&(!max||Number(v.precio)<=Number(max))&&(!estado||v.estado===estado));
  $("searchCount").textContent=`${lista.length} vehículo(s) encontrado(s)`;renderVehiculos($("searchResults"),lista);
 }catch(e){toast(e.message);}
}
async function cargarUsuarios(){
 const lista=$("usersList"),mensaje=$("usersMessage");lista.replaceChildren();mensaje.textContent="Cargando usuarios...";
 try{
  const usuarios=await api("/usuarios");mensaje.textContent=`${usuarios.length} usuario(s) registrado(s)`;
  for(const u of usuarios){
   const fila=document.createElement("div");fila.className=`user-row ${u.activo?"":"inactive"}`;
   const esMiCuenta=u.id===usuario?.id;
   fila.innerHTML=`<div><strong>${escapeHTML(u.nombre)}${esMiCuenta?" (Tú)":""}</strong><p>${escapeHTML(u.email)}</p><p>${u.activo?"Cuenta activa":"Cuenta desactivada"}</p></div><div class="user-row-controls"><select aria-label="Rol de ${escapeHTML(u.nombre)}" ${esMiCuenta?"disabled":""}><option value="usuario" ${u.rol==="usuario"?"selected":""}>Usuario</option><option value="admin" ${u.rol==="admin"?"selected":""}>Administrador</option></select><button type="button" ${esMiCuenta?"disabled":""}>${u.activo?"Desactivar":"Activar"}</button></div>`;
   const selector=fila.querySelector("select"),boton=fila.querySelector("button");
   selector.addEventListener("change",async()=>{
    if(!confirm(`¿Cambiar el rol de ${u.nombre} a ${selector.value}?`)){selector.value=u.rol;return;}
    selector.disabled=true;
    try{await api(`/usuarios/${u.id}`,{method:"PATCH",body:JSON.stringify({rol:selector.value})});toast("Rol actualizado");await cargarUsuarios();}
    catch(e){toast(e.message);await cargarUsuarios();}
   });
   boton.addEventListener("click",async()=>{
    if(!confirm(`¿${u.activo?"Desactivar":"Activar"} la cuenta de ${u.nombre}?`))return;
    boton.disabled=true;
    try{await api(`/usuarios/${u.id}`,{method:"PATCH",body:JSON.stringify({activo:!u.activo})});toast("Estado de cuenta actualizado");await cargarUsuarios();}
    catch(e){toast(e.message);await cargarUsuarios();}
   });
   lista.appendChild(fila);
  }
 }catch(e){mensaje.textContent=`No se pudo consultar usuarios: ${e.message}`;}
}
$("userForm").addEventListener("submit",async event=>{
 event.preventDefault();if(!esAdmin())return;
 const form=event.currentTarget,boton=$("saveUserButton"),mensaje=$("userFormMessage");
 const datos=Object.fromEntries(new FormData(form).entries());boton.disabled=true;mensaje.textContent="Creando usuario...";
 try{await api("/usuarios",{method:"POST",body:JSON.stringify(datos)});form.reset();mensaje.textContent="Empleado registrado correctamente.";toast("Usuario creado");await cargarUsuarios();}
 catch(e){mensaje.textContent=e.message;}
 finally{boton.disabled=false;}
});

$("loginForm").addEventListener("submit",async event=>{
 event.preventDefault();$("loginError").textContent="";
 const credenciales={email:$("loginEmail").value,contraseña:$("loginPassword").value};
 try{
  const r=await fetch("/login",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(credenciales)});const datos=await r.json();
  if(!r.ok||!datos.access_token)throw new Error("Correo o contraseña incorrectos.");
  localStorage.setItem(tokenKey,datos.access_token);await iniciar();
 }catch(e){$("loginError").textContent=e.message;}
});
$("logoutButton").addEventListener("click",()=>salir());
document.querySelectorAll(".nav-item[data-section]").forEach(a=>a.addEventListener("click",e=>{e.preventDefault();if(a.dataset.section==="agregar")abrirFormulario();else irA(a.dataset.section);}));
[["verVehiculosButton","vehiculos"],["verTodosButton","vehiculos"]].forEach(([id,s])=>$(id).addEventListener("click",()=>irA(s)));
$("agregarVehiculoButton").addEventListener("click",()=>abrirFormulario());
$("nuevoDesdeInventario").addEventListener("click",()=>abrirFormulario());
$("cancelVehicleForm").addEventListener("click",()=>irA("vehiculos"));
$("vehicleForm").addEventListener("submit",guardarVehiculo);
$("searchForm").addEventListener("submit",e=>{e.preventDefault();buscar();});
$("clearSearch").addEventListener("click",()=>{$("searchForm").reset();buscar();});
$("closeDetail").addEventListener("click",()=>$("detailModal").classList.add("hidden"));
$("detailModal").addEventListener("click",e=>{if(e.target===$("detailModal"))$("detailModal").classList.add("hidden");});
document.addEventListener("keydown",e=>{if(e.key==="Escape")$("detailModal").classList.add("hidden");});
iniciar();
