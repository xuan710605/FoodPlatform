import { useState } from 'react'
import type { AddressWrite, ApiAddress } from '../../services/commerce'

const emptyAddress:AddressWrite={
  receiver_name:'',
  receiver_phone:'',
  province:'',
  city:'',
  district:'',
  detail_address:'',
  postal_code:null,
  is_default:false,
}

export function AddressForm({initial,onSubmit,onCancel,submitting=false}:{initial?:ApiAddress|null;onSubmit:(value:AddressWrite)=>void;onCancel:()=>void;submitting?:boolean}){
 const [form,setForm]=useState<AddressWrite>(initial?{receiver_name:initial.receiver_name,receiver_phone:initial.receiver_phone,province:initial.province,city:initial.city,district:initial.district,detail_address:initial.detail_address,postal_code:initial.postal_code,is_default:initial.is_default}:emptyAddress)
 const field=(key:keyof AddressWrite,value:string|boolean|null)=>setForm(current=>({...current,[key]:value}))
 const valid=Boolean(form.receiver_name&&form.receiver_phone&&form.province&&form.city&&form.district&&form.detail_address)
 return <><div className="form-grid"><div className="field"><label>收货人</label><input className="input" value={form.receiver_name} onChange={event=>field('receiver_name',event.target.value)}/></div><div className="field"><label>手机号</label><input className="input" value={form.receiver_phone} onChange={event=>field('receiver_phone',event.target.value)}/></div><div className="field"><label>省份</label><input className="input" value={form.province} onChange={event=>field('province',event.target.value)}/></div><div className="field"><label>城市</label><input className="input" value={form.city} onChange={event=>field('city',event.target.value)}/></div><div className="field"><label>区县</label><input className="input" value={form.district} onChange={event=>field('district',event.target.value)}/></div><div className="field"><label>邮政编码</label><input className="input" value={form.postal_code||''} onChange={event=>field('postal_code',event.target.value||null)}/></div><div className="field span-2"><label>详细地址</label><input className="input" value={form.detail_address} onChange={event=>field('detail_address',event.target.value)}/></div><label className="checkbox span-2"><input type="checkbox" checked={form.is_default} onChange={event=>field('is_default',event.target.checked)}/>设为默认地址</label></div><div className="modal-footer" style={{padding:'18px 0 0',marginTop:18}}><button className="btn ghost" onClick={onCancel}>取消</button><button className="btn primary" disabled={!valid||submitting} onClick={()=>onSubmit(form)}>{submitting?'正在保存…':'保存地址'}</button></div></>
}
