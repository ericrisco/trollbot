import random, sys
import interface
 
SUFFICIENT_ENERGY = 1000
MAXIMUM_DISTANCE = 10000
MINIMUM_LIGHTHOUSE_ENERGY = 10
LOOK_FAR_ENERGY = 3
 
class Trollbot(interface.Bot):
    NAME = "Tr0llbot"
 
    def run(self):
        state = self._recv()
        self.map = state["map"]
 
    def play(self, state):
       
        actualPosition = tuple(state["position"])
 
        lighthouses = self.getLighthouses(state)
 
        #Estamos en un faro
        if actualPosition in lighthouses:
            #Estamos en un faro y es nuestro, crear connexion!
            if lighthouses[actualPosition]["owner"] == self.player_num:
                connections = self.permittedLighthousesConnections(state)
                if connections:
                    return self.connect(connections[0])
            elif state["energy"] > MINIMUM_LIGHTHOUSE_ENERGY:
                return self.attack(state["energy"])
 
        nextPosition = self.nextPosition(state)
        return self.move(*nextPosition)
 
    #Obtener el listado de faros
    def getLighthouses(self, state):
        lighthouses = dict((tuple(lighthouse["position"]), lighthouse)
            for lighthouse in state["lighthouses"])
        return lighthouses
 
    #Devuelve las connexiones a los faros permitidos
    def permittedLighthousesConnections(self, state):
 
        connections = []
        lighthouses = self.getLighthouses(state)
 
        actualPosition = state["position"]
       
        #Intentaremos devolver siempre los faros permitidos. Hay que filtrar
        for lighthouse in lighthouses:
 
            #El otro faro no es nuesto
            if lighthouses[lighthouse]["owner"] != self.player_num:
                continue
 
            #No se puede connectar con uno mismo
            if lighthouses[lighthouse]["position"] == actualPosition:
                continue
 
            #No tenemos la llave
            if not lighthouses[lighthouse]["have_key"]:
                continue
 
            #La connexion ya existe
            positions = []
            positions.append(actualPosition)
            if positions in lighthouses[lighthouse]["connections"]:
                continue
           
            connections.append(lighthouse)
 
        return connections
 
    #Calculamos la mejor opcion hacia devemos movernos
    def nextPosition(self, state):
 
        #Tenemos dos opciones, o recoger energia o dirigirnos a un faro
        #Para capturar un faro necesitamos bastante energia, cogemos toda la que podamoswqw
 
        if state["energy"] > SUFFICIENT_ENERGY:
            return self.moveToLighthouse(state)
        else:
            return self.moveToGetEnergy(state)
 
    #Buscar posibles movimientos
    def getPermittedMovements(self, state):
 
        actualX, actualY = state["position"]
 
        moves = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
       
        #Eliminar movimientos que no se pueden hacer
        moves = [(x,y) for x,y in moves if self.map[actualY+y][actualX+x]]
        return moves    
 
    #Buscar el faro mas cercano que no sea nuestro
    def moveToLighthouse(self, state):
 
        lighthouses =self.getLighthouses(state)
        #Cogemos inicialmente el faro que mas rabia nos da
        destination = random.choice(self.getPermittedMovements(state))
 
        for lighthouse in lighthouses:
            if lighthouses[lighthouse]["owner"] != self.player_num:
                #Si hay algun faro de otro jugador se lo robamos!
                destination = lighthouse
            elif not lighthouses[lighthouse]["have_key"]:
                #Si hay algun faro que aun no tenemos la llave
                destination = lighthouse  
 
        moves = self.getPermittedMovements(state)
 
        actualPosition = state["position"]
 
        lighthouse_map = self.getMapDistanceFromPoint(state, lighthouse)
 
        distances = {
            move : lighthouse_map[move[1] + actualPosition[1]][move[0] + actualPosition[0]] - random.uniform(0.1, 0.5)
                for move in moves
        }
 
        move = min(distances, key=distances.get)
 
        return move
 
    #Obtener mapa con la distancia de cada punto a un faro en concreto
    def getMapDistanceFromPoint(self, state, point):
 
        #Crear mapa, valor -1 no valido!
        point_map = [[ MAXIMUM_DISTANCE if p else -1
                                for p in line]
                                for line in self.map]
 
        point_map[point[1]][point[0]] = 0
 
        moves = self.getPermittedMovementsFromPoint(state, point, point_map)
       
        distance_from_point = 0
 
        while len(moves) > 0:
           
            #Asignar distancia desde el faro
            distance_from_point += 1
            for point in points:
                x,y = point
                point_map[y][x] = distance_from_point
 
            next_moves = []
            for point in points:
                int_points = self.getPermittedMovementsFromPoint(state, lighthouse, lighthouse_map)
                next_moves.extend(next_moves)
 
            moves = list(set(next_moves))
 
        return point_map
               
    #Buscar posibles des de un faro
    def getPermittedMovementsFromPoint(self, state, point, lighthouse_map):
 
        actualX, actualY = point
 
        moves = ((-1,-1),(-1,0),(-1,1),(0,-1),(0,1),(1,-1),(1,0),(1,1))
       
        #Eliminar movimientos que no se pueden hacer o que ya estan calculadors
        moves = [(x,y) for x,y in moves if self.map[actualY+y][actualX+x] and lighthouse_map[actualY+y][actualX+x]!=MAXIMUM_DISTANCE]
        return moves      
 
    #Intentar recoger el maximo de energia
    def moveToGetEnergy(self, state):
 
        actualPosition = state["position"]
 
        moves = self.getPermittedMovements(state)
 
        view = state["view"]
 
        #Buscar el centroide de los faros
 
        lighthouses = self.getLighthouses(state)
 
        x = [lighthouse[0] for lighthouse in lighthouses]
        y = [lighthouse[1] for lighthouse in lighthouses]
        centroid = (sum(x) / len(lighthouses), sum(y) / len(lighthouses))
 
        distance_map = self.getMapDistanceFromPoint(state, centroid)
 
        distances = {
            move : distance_map[move[1] + actualPosition[1]][move[0] + actualPosition[0]] + random.uniform(0, 0.2)
                for move in moves
        }
 
        bestMove = min(distances, key=distances.get)
 
        return bestMove
       
 
if __name__ == "__main__":
    iface = interface.Interface(Trollbot)
    iface.run()