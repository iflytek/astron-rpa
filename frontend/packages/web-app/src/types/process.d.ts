declare namespace PROCESS {

  declare namespace AST {

    interface ASTNode<T = string> {
      id: T
      type: NodeType
    }

    interface ContainerNode<T = string> extends ASTNode<T> {
      body: ASTNode<T>[]
    }

    interface RootNode extends ContainerNode<null> {
      type: 'root'
    }

    interface IfNode extends ContainerNode<string | null> {
      type: 'if'
      body: ASTNode[]
      elseifs: ElseIfNode[]
      else: ElseNode[]
      ifend: EndIfNode | null
    }

    interface ElseIfNode extends ContainerNode {
      type: 'elseif'
      body: ASTNode[]
    }

    interface ElseNode extends ContainerNode {
      type: 'else'
      body: ASTNode[]
    }

    interface EndIfNode extends ASTNode {
      type: 'ifend'
    }

    interface GroupNode extends ContainerNode<string> {
      type: 'group'
      body: ASTNode[]
      groupEnd: GroupEndNode | null
    }

    interface GroupEndNode extends ASTNode {
      type: 'groupend'
    }

    interface TryNode extends ContainerNode<string | null> {
      type: 'try'
      body: ASTNode[]
      catch: ExceptNode[]
      finally: FinallyNode[]
      tryEnd: EndTryNode | null
    }

    interface CatchNode extends ContainerNode {
      type: 'catch'
      finally: FinallyNode[]
      body: ASTNode[]
    }

    interface FinallyNode extends ContainerNode {
      type: 'finally'
      body: ASTNode[]
    }

    interface EndTryNode extends ASTNode {
      type: 'tryend'
    }

    interface ForNode extends ContainerNode<string | null> {
      type: 'stepfor' | 'listfor' | 'dictfor' | 'excelcontentfor' | 'borsimilarfor' | 'datatablefor'
      body: ASTNode[]
      forEnd: EndWhileNode | null
    }

    interface WhileNode extends ContainerNode<string | null> {
      type: 'while'
      body: ASTNode[]
      forEnd: EndWhileNode | null
    }

    interface EndWhileNode extends ASTNode {
      type: 'forend'
    }

    interface ProcessNode {
      id: string
      type: NodeType
      level?: number
      // data: any
    }
  }

  declare namespace LIST {

    interface AbilityItem {
      [key: string]: any
    }
  }
}
