import type { Element, ElementGroup, GlobalVariable, Process, ProcessNode, Robot as Project, PythonPackage } from './type'

/**
 * NOTE: VM 表示 ViewModel，也就是业务层的数据。
 * 主要是为了区分逻辑，防止业务层和逻辑层混淆，特别是在业务层直接修改逻辑层的数据。
 * 当前只是简单地设置为了 readonly，做了修改保护。
 * 后续可以根据业务需要，进行精简，或者转换。
 * !!! 为了节省内存，当前逻辑层实现层面没有做拷贝，所以业务层需要严格控制数据的修改，不能绕过。
 */

export type ElementVM = Readonly<Element>
export type ElementGroupVM = Readonly<ElementGroup>
export type GlobalVariableVM = Readonly<GlobalVariable>
export type ProcessVM = Readonly<Process>
export type ProcessNodeVM = Readonly<ProcessNode>
export type PythonPackageVM = Readonly<PythonPackage>
export type ProjectVM = Readonly<Project>
